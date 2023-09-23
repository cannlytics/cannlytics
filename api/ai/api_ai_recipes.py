"""
BudderBaker AI Views | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/2/2023
Updated: 2/8/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with AI-generated cannabis recipes.

Future work:

    [ ] Optionally get a new title for the recipe when updating it.
    [ ] Make search queries more robust to known query limitations.
    [ ] Integrate CoADoc for COA parsing.
    [ ] Integrate SkunkFx for effects and aromas prediction.
    [ ] Delete the `recipe_reviews` doc in full when deleting reviews.
    [ ] Calculate average rating and number of reviews.
    [ ] Save / archive multiple images?

"""
# Standard imports:
from datetime import datetime
import os
import secrets
import tempfile

# External imports:
import google.auth
from google.cloud.firestore import Increment
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports:
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    delete_document,
    delete_file,
    download_file,
    get_document,
    get_collection,
    get_file_url,
    update_document,
    update_documents,
    upload_file,
)
from cannlytics.utils import convert_to_numeric, download_file_from_url


# API defaults.
AUTH_ERROR = 'Authentication failed. Please login to Cannlytics\
 (https://cannlytics.com) or provide a valid Cannlytics API key\
 in an `Authentication: Bearer <token>` header.'

# OpenAI defaults.
CREATE_TEXT_MODEL = 'text-davinci-003'
EDIT_TEXT_MODEL = 'text-davinci-edit-001'
IMAGE_SIZE = '1024x1024' # 256x256, 512x512, or 1024x1024
MAX_TOKENS = 1_000 # The maximum number of OpenAI tokens per request.
TEMPERATURE = 0.5 # The default value for creativity.
TOKENS_PER_IMAGE = 1_000 # The davinci equivalent of tokens.

# Prompt defaults.
DEFAULT_PRODUCT = 'cannabis edibles'
DEFAULT_TOTAL_THC = 800
DEFAULT_TOTAL_CBD = 0
IMAGE_TYPE = 'drawing'
UPDATE_INSTRUCTIONS = 'a large change'

# Firebase defaults.
ID_LENGTH = 16
LIMIT = 1_000
ORDER_BY = 'updated_at'


def initialize_openai() -> None:
    """Initialize OpenAI."""
    _, project_id = google.auth.default()
    openai_api_key = access_secret_version(
        project_id=project_id,
        secret_id='OPENAI_API_KEY',
        version_id='latest',
    )
    openai.api_key = openai_api_key


def increment_usage(usage, prompt_ids, response):
    """Increment a user's OpenAI usage and record prompt IDs."""
    try:
        usage += response['usage']['total_tokens']
        prompt_ids.append(response['id'])
    except:
        pass
    return usage, prompt_ids


def get_recipes(params, recipe_id=None, uid=None) -> list:
    """Get public or user recipes. Allows user to pass an `operation`
    parameter to apply to non-date filters. Operators include:
        `==`, `>=`, `<=`, `>`, `<`, `!=`, `in`, `not_in`,
        `array_contains`, `array_contains_any`.
    """
    # Get query parameters.
    public = params.get('public', recipe_id)
    limit = params.get('limit', LIMIT)
    operation = params.get('operation', '==')
    order_by = params.get('order_by', ORDER_BY)
    desc = params.get('desc', True)
    filters = []

    # Add any filters.
    # TODO: Make filters more robust to potential errors.
    available_filters = [
        {'key': 'product_name', 'type': 'str'},
        {'key': 'product_subtype', 'type': 'str'},
        {'key': 'title', 'type': 'str'},
        {'key': 'total_thc', 'type': 'float'},
        {'key': 'total_cbd', 'type': 'float'},
        {'key': 'serving_cbd', 'type': 'float'},
        {'key': 'number_of_servings', 'type': 'number_of_servings'},
        {'key': 'created_at_min', 'type': 'datetime'},
        {'key': 'created_at_max', 'type': 'datetime'},
        {'key': 'updated_at_min', 'type': 'datetime'},
        {'key': 'updated_at_max', 'type': 'datetime'},
    ]
    for param in available_filters:

        # Get any filters the user may have passed.
        value = params.get(param['key'])
        if value:
            key = param['key']

            # Add any starting time filter.
            if '_min' in key:
                filters.append({
                    'key': key.replace('_min', ''),
                    'value': value,
                    'operation': '>=',
                })

            # Add any ending time filter.
            elif '_max' in key:
                filters.append({
                    'key': key.replace('_max', ''),
                    'value': value,
                    'operation': '<=',
                })
            
            # Add any other filters.
            else:
                filters.append({
                    'key': key,
                    'value': value,
                    'operation': operation,
                })

    # Get community-created recipes.
    if public == True or public == 'public':
        collection = 'public/ai/recipes'
        recipes = get_collection(
            collection,
            limit=limit,
            order_by=order_by,
            desc=desc,
            filters=filters,
        )

    # Get a recipe the user has created.
    elif recipe_id:
        ref = f'users/{uid}/recipes/{recipe_id}'
        doc = get_document(ref)
        recipes = [doc]

    # Search for recipes (queries).
    else:
        collection = f'users/{uid}/recipes'
        recipes = get_collection(
            collection,
            limit=limit,
            order_by=order_by,
            desc=desc,
            filters=filters,
        )
    
    # Return any found recipes.
    return recipes


def create_recipe(uid, data):
    """Create a recipe with OpenAI."""

    # Initialize a blank recipe.
    usage, prompt_ids = 0, []
    recipe_id = secrets.token_hex(ID_LENGTH)
    ref = f'users/{uid}/recipes/{recipe_id}'

    # Get the posted data.
    ingredients = data.get('ingredients', [])
    product_type = data.get('product_type')
    product_name = data.get('product_name', DEFAULT_PRODUCT)
    special_instructions = data.get('special_instructions')
    doses = data.get('doses')
    image_type = data.get('image_type', IMAGE_TYPE).lower()
    total_thc = data.get('total_thc', DEFAULT_TOTAL_THC)
    total_cbd = data.get('total_cbd', DEFAULT_TOTAL_CBD)
    public = data.get('public', False)
    temperature = data.get('creativity', TEMPERATURE)

    # Update Firestore to indicate that the recipe is being created.
    update_document(ref, {
        'baking': True,
        'creativity': temperature,
        'doses': doses,
        'ingredients': ingredients,
        'product_type': product_type,
        'product_name': product_name,
        'special_instructions': special_instructions,
        'doses': doses,
        'image_type': image_type,
        'total_thc': total_thc,
        'total_cbd': total_cbd,
        'public': public,
        'version': 1,
        'created_by': uid,
    })

    # Create a recipe for cannabis edibles, optionally given
    # ingredients, a desired product, and/or the desired dose
    # of various compounds. e.g. {"name": "THC", "units": "mg", "value": 800}.
    recipe_prompt = 'Write a recipe'
    if product_name:
        recipe_prompt += f' with {product_name}'

    # Assign product type.
    if product_type is None:
        product_type = '???'
    else:
        recipe_prompt += f' ({product_type} cannabis)'

    # Future work: Get lab results with CoADoc if possible.
    # The user could pass a `results_image`.

    # TODO: Paid product names with ingredients where possible.

    # Get any specified dose of compounds.
    if doses:
        recipe_prompt += '\nWith:'
        for dose in doses:
            units = dose['units']
            value = dose['value']
            name = dose['name']
            recipe_prompt += f'\n{value} {units} of {name}'
            if '/' in units:
                recipe_prompt += ' per serving'

        # TODO: Pair any known terpenes with ingredients.

    # Get any special instructions.
    if special_instructions:
        recipe_prompt += '\nWith special instructions: '
        recipe_prompt += special_instructions

    # Get any specified ingredients.
    if ingredients:
        recipe_prompt += '\nIngredients:'
        for ingredient in ingredients:
            recipe_prompt += f'\n{ingredient}'

    # Prompt GPT for instructions.
    recipe_prompt += '\nInstructions:'

    # Initialize OpenAI.
    initialize_openai()

    # Ask GPT to create a recipe.
    try:
        print(recipe_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=recipe_prompt,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        recipe = response['choices'][0]['text']
    except:
        message = 'Failed to generate a recipe.'
        return message, None, None

    # Ask GPT for a fun title.
    try:
        if temperature > 0.5:
            title_prompt = 'Write a fun title for the following recipe'
            title_prompt += ' (pun if possible)'
        else:
            title_prompt = 'Write a title for the following recipe'
        title_prompt += ' (use the product name if possible):'
        title_prompt += recipe
        print(title_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=title_prompt,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        product_title = response['choices'][0]['text'] \
            .replace('\n', ' ').replace('"', '').strip()
    except:
        product_title = product_name.title()

    # Ask GPT if it is a food or a drink to differentiate
    # between solid and liquid edibles.
    try:
        type_prompt = 'Is this recipe for a food or drink? '
        type_prompt += product_title
        type_prompt += '\nType:'
        print(type_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=type_prompt,
            max_tokens=MAX_TOKENS,
            temperature=0,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        edible_type = response['choices'][0]['text'] \
            .replace('\n', ' ').replace('"', '').strip()
        if edible_type.lower() == 'drink':
            product_subtype = 'liquid_edible'
        else:
            product_subtype = 'solid_edible'
    except:
        product_subtype = None

    # Determine the units.
    if product_subtype == 'liquid_edible':
        units = 'ml'
        units_name = 'milliliters'
    else:
        units = 'mg'
        units_name = 'milligrams'

    # Ask GPT for a description of the recipe.
    try:
        if temperature >= 0.5:
            description_prompt = 'Fun, short summary of:'
        else:
            description_prompt = 'Short summary of:'
        description_prompt += recipe
        print(description_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=description_prompt,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        description = response['choices'][0]['text'] \
            .replace('\n', ' ').replace('"', '').strip()
    except:
        description = None

    # Get an image for the recipe.
    # Lets the user specify the type of image.
    # E.g. `drawing` or `high-quality photo`.
    image_url, image_ref, file_url = None, None, None
    try:
        image_prompt = f'A {image_type} of '
        image_prompt += product_title
        print(image_prompt)
        response = openai.Image.create(
            prompt=image_prompt,
            n=1,
            size=IMAGE_SIZE,
            user=uid,
        )
        print(response)
        usage += TOKENS_PER_IMAGE
        image_url = response['data'][0]['url']

        # Download the image and save the image to Firebase Storage.
        print('Downloading image...')
        tempfile.gettempdir()
        image_file = download_file_from_url(
            image_url,
            tempfile.gettempdir(),
            file_name='recipe.png',
        )

        # Upload the image to storage.
        print('Uploading image to storage...')
        image_ref = f'users/{uid}/recipes/{recipe_id}.png'
        _, project_id = google.auth.default()
        bucket_name = f'{project_id}.appspot.com'
        upload_file(image_ref, image_file, bucket_name=bucket_name)
        file_url = get_file_url(image_ref, bucket_name=bucket_name)
        print('Uploaded image to storage')
    except:
        pass

    # Ask GPT for the total weight in milligrams of the whole dish.
    total_weight = '???'
    try:
        total_prompt = f'What is the total weight in {units_name} of the following recipe?'
        total_prompt += recipe
        total_prompt += f'\nTotal {units_name}:'
        print(total_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=total_prompt,
            max_tokens=MAX_TOKENS,
            temperature=0,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        total_weight = response['choices'][0]['text'] \
            .replace('\n', ' ').replace('"', '').strip()
        try:
            total_weight = convert_to_numeric(total_weight, strip=True)
        except:
            pass
    except:
        pass

    # Ask GPT for the weight per serving in milligrams.
    print('Calculating serving weight...')
    serving_weight = '???'
    try:
        serving_prompt = f'What is the {units_name} per serving (or each) of the following recipe?'
        serving_prompt += recipe
        serving_prompt += f'\n{units_name} per serving (or each):'
        print(serving_prompt)
        response = openai.Completion.create(
            model=CREATE_TEXT_MODEL,
            prompt=serving_prompt,
            max_tokens=MAX_TOKENS,
            temperature=0,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        serving_weight = response['choices'][0]['text'] \
            .replace('\n', ' ').replace('"', '').strip()
        try:
            serving_weight = convert_to_numeric(serving_weight, strip=True)
        except:
            pass
    except:
        pass

    # Estimate the number of servings.
    print('Calculating the number of servings...')
    try:
        number_of_servings = round(total_weight / serving_weight)
    except:
        number_of_servings = '???'

    # Future work: Handle other unit types.
    # Currently the calculations below assume mg.

    # Calculate total THC per serving.
    # Default: 1 gram of oil (1000mg) at 80% THC is 800mg THC.
    print('Calculating total THC per serving...')
    try:
        serving_thc = total_thc / number_of_servings
    except:
        serving_thc = '???'
    
    # Calculate total CBD per serving.
    print('Calculating total CBD per serving...')
    try:
        serving_cbd = total_cbd / number_of_servings
    except:
        serving_cbd = '???'

    # Future work: Use SkunkFx to predict effects and aromas.
            
    # Compile the data.
    # Future work: Also keep track of terpenes?
    print('Compiling data...')
    timestamp = datetime.now().isoformat()
    entry = {
        'baking': False,
        'description': description,
        'file_url': file_url,
        'image_ref': image_ref,
        'image_url': image_url,
        'image_type': image_type,
        'product_subtype': product_subtype,
        'recipe': recipe,
        'title': product_title,
        'number_of_servings': number_of_servings,
        'total_weight': total_weight,
        'serving_weight': serving_weight,
        'serving_thc': serving_thc,
        'serving_cbd': serving_cbd,
        'units': units,
        'created_at': timestamp,
        'updated_at': timestamp,
    }
    refs, entries = [ref], [entry]

    # Allow the user to make their recipe public.
    try:
        if public:
            refs.append(f'public/ai/recipes/{recipe_id}')
            entries.append(entry)
    except:
        print("Couldn't make recipe public.")

    # Record usage and prompt IDs for administrators to review.
    try:
        doc_id = secrets.token_hex(ID_LENGTH)
        refs.append(f'admin/ai/recipe_usage/{doc_id}')
        entries.append({'usage': usage, 'prompt_ids': prompt_ids})
    except:
        print("Couldn't save admin document.")

    # Return the Firestore data.
    return entry, refs, entries


def update_recipe(uid, recipe_id, data, params=None):
    """Update an existing recipe with OpenAI."""

    # Initialize an update for the recipe.
    usage, prompt_ids = 0, []
    initialize_openai()
    if params is None:
        temperature = TEMPERATURE
    else:
        temperature = params.get('creativity', TEMPERATURE)

    # Get the existing recipe
    ref = f'users/{uid}/recipes/{recipe_id}'
    doc = get_document(ref)
    if not doc:
        return None, None, None

    # Update Firestore to indicate that the recipe is being updated.
    update_document(ref, {'baking': True})

    # Get the existing data.
    existing_recipe = doc['recipe']
    product_title = data.get('title', doc['title'])
    change_recipe = data.get('change_recipe', True)
    change_image = data.get('change_image', False)

    # TODO: Get a new title for the recipe.
    

    # Ask GPT to update the existing recipe.
    # Handles changes where the user doesn't want the recipe to change.
    if change_recipe:
        instructions = 'Given:'
        instructions += data.get('special_instructions', UPDATE_INSTRUCTIONS)
        instructions += '\nChange the recipe'
        print(instructions)
        response = openai.Edit.create(
            model=EDIT_TEXT_MODEL,
            input=existing_recipe,
            instruction=instructions,
            temperature=temperature,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        updated_recipe = response['choices'][0]['text']
    else:
        updated_recipe = existing_recipe

    # Ask GPT Create a variation of an existing image.
    # Handles changes where the user doesn't want the image to change.
    if change_image:
        _, project_id = google.auth.default()
        bucket_name = f'{project_id}.appspot.com'
        image_file = os.path.join(tempfile.gettempdir(), 'recipe.png')
        download_file(doc['image_ref'], image_file, bucket_name=bucket_name)
        response = openai.Image.create_variation(
            image=open(image_file, 'rb'),
            n=1,
            size=IMAGE_SIZE,
            user=uid,
        )
        print(response)
        usage += TOKENS_PER_IMAGE
        image_url = response['data'][0]['url']
    
        # Download the image and save the image to Firebase Storage.
        # Future work: Save / archive multiple images?
        tempfile.gettempdir()
        image_file = download_file_from_url(
            image_url,
            tempfile.gettempdir(),
            file_name='recipe.png',
        )
        image_ref = f'users/{uid}/recipes/{recipe_id}.png'
        _, project_id = google.auth.default()
        bucket_name = f'{project_id}.appspot.com'
        upload_file(image_ref, image_file, bucket_name=bucket_name)
        file_url = get_file_url(image_ref, bucket_name=bucket_name)
    else:
        file_url = doc['file_url']
        image_url = doc['image_url']
    
    # Allow the user to change their recipes to/from public.
    public = data.get('public', doc['public'])

    # Compile data.
    # When updating recipes, increment the version number.
    ref = f'users/{uid}/recipes/{recipe_id}'
    entry = {
        **doc,
        'baking': False,
        'update_instructions': instructions,
        'creativity': temperature,
        'file_url': file_url,
        'image_url': image_url,
        'recipe': updated_recipe,
        'version': Increment(1),
        'public': public,
        'updated_at': datetime.now().isoformat(),
    }

    # Prepare the data for Firestore.
    refs, entries = [ref], [entry]

    # Either remove or update the recipe from public recipes.
    public_ref = f'public/ai/recipes/{recipe_id}'
    if public:
        refs.append(public_ref)
        entries.append(entry)
    else:
        try:
            delete_document(public_ref)
        except:
            pass

    # Record usage and prompt IDs for administrators to review.
    doc_id = secrets.token_hex(ID_LENGTH)
    refs.append(f'admin/ai/recipe_usage/{doc_id}')
    entries.append({
        'usage': usage,
        'prompt_ids': prompt_ids,
        'uid': uid,
    })

    # Return the data.
    return entry, refs, entries


def add_recipe_feedback(uid, recipe_id, data):
    """Create a feedback document for administrators to review."""
    doc_id = secrets.token_hex(ID_LENGTH)
    feedback_ref = f'admin/ai/recipe_feedback/{doc_id}'
    entry = {
        'uid': uid,
        'recipe_id': recipe_id,
        'feedback': data.get('feedback'),
        'like': data.get('like'),
        'created_at': datetime.now().isoformat(),
    }
    refs, entries = [feedback_ref], [entry]
    return entry, refs, entries


def add_recipe_review(uid, recipe_id, data):
    """Create or update a user's review of a recipe.
    """
    # Get the existing recipe.
    public_ref = f'public/ai/recipes/{recipe_id}'
    doc = get_document(public_ref)
    if not doc:
        return None, None, None
    
    # Get the user's posted review.
    # Allows user's to delete their own reviews by passing null.
    # Future work: Delete the `recipe_reviews` doc in full.
    try:
        entry = {'review': data['review']}
    except:
        entry = {}

    # Get the user's rating.
    rating = data.get('rating')
    if rating is not None:
        entry['rating'] = rating

    # Future work: Calculate average rating and number of reviews.

    # Save the user's rating and review in Firestore.
    review_ref = f'{public_ref}/recipe_reviews/{uid}'
    refs, entries = [review_ref], [entry]
    return entry, refs, entries


def delete_recipe(uid, recipe_id):
    """Delete a user's recipe.
    """
    # Get the existing recipe.
    ref = f'users/{uid}/recipes/{recipe_id}'
    doc = get_document(ref)
    if not doc:
        return None

    # Delete the recipe image.
    _, project_id = google.auth.default()
    bucket_name = f'{project_id}.appspot.com'
    delete_file(doc['image_ref'], bucket_name=bucket_name)

    # Delete the recipe.
    delete_document(ref)

    # Delete the recipe from public recipes.
    try:
        public_ref = f'public/ai/recipes/{recipe_id}'
        delete_document(public_ref)
    except:
        pass

    # Return the delete data.
    return doc


# === Recipes API endpoint ===

@api_view(['GET', 'POST'])
def recipes_api(request: Request, recipe_id=None):
    """Get, create, update, and delete AI-generated recipes."""

    # Authenticate the user.
    # Requires the user to pass a `CANNLYTICS_API_KEY`.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    uid = claims['uid']
    print('Request by:', uid)
    params = request.query_params
    data = request.data.get('data', request.data)
    recipe_id = data.get('id', recipe_id)
    action = request.query_params.get('action', data.get('action'))

    # Get recipe(s).
    if request.method == 'GET':

        # Query recipes.
        recipes = get_recipes(params, recipe_id=recipe_id, uid=uid)

        # Return any found recipes.
        response = {'success': True, 'data': recipes}
        return Response(response, status=200)

    # Create, update, review, and discuss recipe(s).
    elif request.method == 'POST':

        # Allow the user to review/rate public recipes.
        if action == 'review':
            entry, refs, entries = add_recipe_review(uid, recipe_id, data)
            if entry is None:
                message = 'Recipe not found among public recipes.'
                response = {'success': False, 'message': message}
                return Response(response, status=404)

        # Allow users to give feedback on recipes.
        elif action == 'feedback':
            entry, refs, entries = add_recipe_feedback(uid, recipe_id, data)
        
        # Create a recipe.
        elif recipe_id is None:
            action = 'create_recipe'
            print('Creating recipe...')
            entry, refs, entries = create_recipe(uid, data)
            # if isinstance(entry, str):
            #     message = 'Failed to create recipe. ' + entry
            #     response = {'success': False, 'message': message}
            #     return Response(response, status=404)

        # Update an existing recipe.
        else:
            action = 'update_recipe'
            print('Updating recipe...')
            entry, refs, entries = update_recipe(uid, recipe_id, data, params)
            if entry is None:
                message = 'Recipe not found among your recipes.'
                response = {'success': False, 'message': message}
                return Response(response, status=404)

        # Save all user, public, and usage data to Firestore.
        try:            
            print('Saving all data to Firestore...')
            update_documents(refs, entries)
        except:
            print('Failed to save data to Firestore.')

        # Create an activity log.
        try:
            print('Creating activity log...')
            create_log(
                ref='logs/ai/recipe_logs',
                claims=claims,
                action=action,
                log_type='recipes',
                key=recipe_id,
                changes=entries
            )
        except:
            print('Failed to log activity.')

        # Return the entered data.
        print('Returning the data...')
        response = {'success': True, 'data': entries}
        return Response(response, status=200)

    # Delete recipe(s).
    elif request.method == 'POST':

        # Delete the recipe data.
        doc = delete_recipe(uid, recipe_id)
        if not doc:
            message = 'Recipe not found among your recipes.'
            response = {'success': False, 'message': message}
            return Response(response, status=404)

        # Create an activity log.
        create_log(
            ref='logs/ai/recipe_logs',
            claims=claims,
            action='delete_recipe',
            log_type='recipes',
            key=recipe_id,
            changes=[doc]
        )

        # Return a success message.
        response = {'success': True, 'data': None}
        return Response(response, status=200)
