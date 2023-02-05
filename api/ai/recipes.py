"""
AI Views | BudderBaker | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/2/2023
Updated: 2/4/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with AI-generated cannabis recipes.

TODO:

    [ ] Keep track of user usage.
    [ ] Keep track of prompts.
    [ ] Archive old images.
    [ ] Integrate CoADoc for COA parsing.
    [ ] Integrate SkunkFx for effects and aromas prediction.

"""
# Standard imports.
from datetime import datetime
import os
import secrets
import tempfile

# External imports.
import google.auth
from google.cloud.firestore import Increment
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports.
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
    update_documents,
    upload_file,
)
from cannlytics.utils import convert_to_numeric, download_file_from_url

# Authentication error message.
AUTH_ERROR = 'Authentication failed. Please login to Cannlytics\
 (https://console.cannlytics.com) or provide a valid Cannlytics API key\
 in an `Authentication: Bearer <token>` header.'

# Model defaults.
DEFAULT_PRODUCT = 'cannabis edibles'
DEFAULT_TOTAL_THC = 800
DEFAULT_TOTAL_CBD = 0
ID_LENGTH = 16
IMAGE_TYPE = 'drawing'
LIMIT = 1000
UPDATE_INSTRUCTIONS = 'a large change'

# The maximum number of OpenAI tokens per request.
MAX_TOKENS = 1_000

# The OpenAI models.
CREATE_MODEL = 'text-davinci-003'
EDIT_MODEL = 'text-davinci-edit-001'
IMAGE_MODEL = ''

# The default value for creativity.
TEMPERATURE = 0.5


def initialize_openai():
    """Initialize OpenAI."""
    _, project_id = google.auth.default()
    openai_api_key = access_secret_version(
        project_id=project_id,
        secret_id='OPENAI_API_KEY',
        version_id='latest',
    )
    openai.api_key = openai_api_key


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
    params = request.query_params
    data = request.data.get('data', request.data)
    recipe_id = data.get('id', recipe_id)

    # Get recipe(s).
    if request.method == 'GET':

        # Get query parameters.
        public = params.get('public', recipe_id)
        limit = params.get('limit', LIMIT)
        order_by = params.get('order_by', 'updated_at')
        desc = params.get('desc', True)
        filters = []

        # TODO: Implement filters.

        # Get community-created recipes.
        if public == True or public == 'public':
            collection = 'public/data/recipes'
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
        response = {'success': True, 'data': recipes}
        return Response(response, status=200)

    # Create or update recipe(s).
    elif request.method == 'POST':

        # Let the user specify the degree of creativity.
        temperature = params.get('temperature', TEMPERATURE)
        
        # Create a recipe.
        usage = 0
        prompt_ids = []
        if recipe_id is None:

            # Create a recipe ID.
            recipe_id = secrets.token_hex(ID_LENGTH)
            ref = f'users/{uid}/recipes/{recipe_id}'

            # Update Firestore to indicate that the recipe is being created.
            update_documents([ref], [{'baking': True}])

            # Create a recipe for cannabis edibles given ingredients, a product,
            # and the desired dose per serving. Get the serving size and number of servings
            # per dish.
            ingredients = data.get('ingredients', [])
            prompt = 'Write a recipe'
            product_name = data.get('product_name', DEFAULT_PRODUCT)
            if product_name:
                prompt += f' for {product_name}'
            doses = data.get('doses')
            if doses:
                prompt += 'With:'
                for dose in doses:
                    units = dose['units']
                    value = dose['value']
                    name = dose['name']
                    prompt += f'\n{value} {units} of {name} per serving'
            if ingredients:
                prompt += '\nIngredients:'
                for ingredient in ingredients:
                    prompt += f'\n{ingredient}'

            prompt += '\nInstructions:'

            # TODO: Get lab results with CoADoc if possible.

            # TODO: Pair terpenes / strains with ingredients where possible.

            # Initialize OpenAI.
            initialize_openai()

            # Ask GPT to create a recipe.
            response = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=prompt,
                max_tokens=MAX_TOKENS,
                temperature=temperature,
                n=1,
                user=uid,
            )
            recipe = response['choices'][0]['text']
            usage += response['usage']['total_tokens']
            prompt_ids.append(response['id'])

            # Ask GPT for a fun title.
            if temperature > 0.5:
                title_prompt = 'Write a fun title for the following recipe'
                title_prompt += ' (pun if possible)'
            else:
                title_prompt = 'Write a title for the following recipe'
            title_prompt += ' (use the product name if possible):'
            title_prompt += recipe
            response2 = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=title_prompt,
                max_tokens=MAX_TOKENS,
                temperature=temperature,
                n=1,
                user=uid,
            )
            product_title = response2['choices'][0]['text'] \
                .replace('\n', ' ').replace('"', '').strip()
            usage += response2['usage']['total_tokens']
            prompt_ids.append(response2['id'])

            # Ask GPT if it is a food or a drink to differentiate
            # between solid and liquid edibles.
            type_prompt = 'Is this recipe for a food or drink?'
            type_prompt += product_title
            type_prompt += 'Type:'
            response7 = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=type_prompt,
                max_tokens=MAX_TOKENS,
                temperature=0,
                n=1,
                user=uid,
            )
            edible_type = response7['choices'][0]['text'] \
                .replace('\n', ' ').replace('"', '').strip()
            if edible_type.lower() == 'drink':
                product_subtype = 'liquid_edible'
            else:
                product_subtype = 'solid_edible'

            # Determine the units.
            if product_subtype == 'liquid_edible':
                units = 'ml'
                units_name = 'milliliters'
            else:
                units = 'mg'
                units_name = 'milligrams'

            # Ask GPT for a description of the recipe.
            if temperature >= 0.5:
                description_prompt = 'Fun, short summary of:'
            else:
                description_prompt = 'Short summary of:'
            description_prompt += recipe
            response3 = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=description_prompt,
                max_tokens=MAX_TOKENS,
                temperature=temperature,
                n=1,
                user=uid,
            )
            description = response3['choices'][0]['text'] \
                .replace('\n', ' ').replace('"', '').strip()
            usage += response3['usage']['total_tokens']
            prompt_ids.append(response3['id'])
            print(description)

            # Get an image for the recipe.
            # Lets the user specify the type of image.
            # E.g. `drawing` or `high-quality photo`.
            image_type = data.get('image_type', IMAGE_TYPE)
            image_prompt = f'A {image_type} of '
            image_prompt += product_title
            response4 = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size='1024x1024'
            )
            image_url = response4['data'][0]['url']

            # Download the image and save the image to Firebase Storage.
            tempfile.gettempdir()
            image_file = download_file_from_url(
                image_url,
                tempfile.gettempdir(),
                ext='.png',
            )
            image_ref = f'users/{uid}/recipes/{recipe_id}.png'
            _, project_id = google.auth.default()
            bucket_name = f'{project_id}.appspot.com'
            upload_file(image_ref, image_file, bucket_name=bucket_name)
            file_url = get_file_url(image_ref, bucket_name=bucket_name)

            # Ask GPT for the total weight in milligrams of the whole dish.
            total_prompt = f'What is the total weight in {units_name} of the following recipe?'
            total_prompt += recipe
            total_prompt += f'\nTotal {units_name}:'
            response5 = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=total_prompt,
                max_tokens=MAX_TOKENS,
                temperature=0,
                n=1,
                user=uid,
            )
            total_weight = response5['choices'][0]['text'] \
                .replace('\n', ' ').replace('"', '').strip()
            try:
                total_weight = convert_to_numeric(total_weight, strip=True)
            except:
                pass
            print(total_weight)

            # Ask GPT for the weight per serving in milligrams.
            serving_prompt = f'What is the {units_name} per serving (or each) of the following recipe?'
            serving_prompt += recipe
            serving_prompt += f'\n{units_name} per serving (or each):'
            response6 = openai.Completion.create(
                model=CREATE_MODEL,
                prompt=serving_prompt,
                max_tokens=MAX_TOKENS,
                temperature=0,
                n=1,
                user=uid,
            )
            serving_weight = response6['choices'][0]['text'] \
                .replace('\n', ' ').replace('"', '').strip()
            try:
                serving_weight = convert_to_numeric(serving_weight, strip=True)
            except:
                pass
            print(serving_weight)

            # Estimate the number of servings.
            try:
                number_of_servings = round(total_weight / serving_weight)
            except:
                number_of_servings = 'Unknown'

            # Calculate total THC per serving.
            # Default: 1 gram of oil (1000mg) at 80% THC is 800mg THC.
            total_thc = data.get('total_thc', DEFAULT_TOTAL_THC)
            try:
                serving_thc = total_thc / number_of_servings
            except:
                serving_thc = 'Unknown'
            
            # Calculate total CBD per serving.
            total_cbd = data.get('total_cbd', DEFAULT_TOTAL_CBD)
            try:
                serving_cbd = total_cbd / number_of_servings
            except:
                serving_cbd = 'Unknown'

            # TODO: Use SkunkFx to predict effects and aromas.
            
            # Save the data in Firestore.
            timestamp = datetime.now().isoformat()
            entry = {
                'description': description,
                'file_url': file_url,
                'image_ref': image_ref,
                'image_url': image_url,
                'product_name': product_name,
                'recipe': recipe,
                'title': product_title,
                'number_of_servings': number_of_servings,
                'total_weight': total_weight,
                'total_weight_units': 'g',
                'serving_weight': serving_weight,
                'serving_weight_units': 'g',
                'total_thc': total_thc,
                'serving_thc': serving_thc,
                'total_cbd': total_cbd,
                'serving_cbd': serving_cbd,
                # TODO: Also keep track of terpenes?
                'units': 'mg',
                'version': 1,
                'created_at': timestamp,
                'updated_at': timestamp,
            }
            update_documents([ref], [entry])
            create_log(
                ref='logs/recipes/recipes_logs',
                claims=claims,
                action='create_recipe',
                log_type='recipes',
                key=recipe_id,
                changes=[entry]
            )

        # Update an existing recipe.
        else:

            # Initialize OpenAI.
            initialize_openai()

            # Get the existing recipe
            ref = f'users/{uid}/recipes/{recipe_id}'
            doc = get_document(ref)
            existing_recipe = doc['recipe']
            product_title = data.get('title', doc['title'])
            change_recipe = data.get('change_recipe', True)
            change_image = data.get('change_image', False)

            # Ask GPT to update the existing recipe.
            # Handles changes where the user doesn't want the recipe to change.
            if change_recipe:
                instructions = 'Given:'
                instructions += data.get('instructions', UPDATE_INSTRUCTIONS)
                instructions += '\nChange the recipe'
                response10 = openai.Edit.create(
                    model=EDIT_MODEL,
                    input=existing_recipe,
                    instruction=instructions,
                    temperature=temperature,
                    n=1,
                )
                updated_recipe = response10['choices'][0]['text']
            else:
                updated_recipe = existing_recipe

            # Ask GPT Create a variation of an existing image.
            # Handles changes where the user doesn't want the image to change.
            if change_image:
                _, project_id = google.auth.default()
                bucket_name = f'{project_id}.appspot.com'
                image_file = os.path.join(tempfile.gettempdir(), 'recipe.png')
                download_file(doc['image_ref'], image_file, bucket_name=bucket_name)
                response9 = openai.Image.create_variation(
                    image=open(image_file, 'rb'),
                    n=1,
                    size='1024x1024'
                )
                image_url = response9['data'][0]['url']
            
                # Download the image and save the image to Firebase Storage.
                # Future work: Save / archive multiple images?
                tempfile.gettempdir()
                image_file = download_file_from_url(
                    image_url,
                    tempfile.gettempdir(),
                    ext='.png',
                )
                image_ref = f'users/{uid}/recipes/{recipe_id}.png'
                _, project_id = google.auth.default()
                bucket_name = f'{project_id}.appspot.com'
                upload_file(image_ref, image_file, bucket_name=bucket_name)
                file_url = get_file_url(image_ref, bucket_name=bucket_name)
            else:
                file_url = doc['file_url']
                image_url = doc['image_url']

            # Save the data in Firestore.
            # When updating recipes, increment the version number.
            uid = claims['uid']
            ref = f'users/{uid}/recipes/{recipe_id}'
            entry = {
                **doc,
                'file_url': file_url,
                'image_url': image_url,
                'recipe': updated_recipe,
                'version': Increment(1),
                'updated_at': datetime.now().isoformat(),
            }
            update_documents([ref], [entry])
            create_log(
                ref='logs/recipes/recipes_logs',
                claims=claims,
                action='create_recipe',
                log_type='recipes',
                key=recipe_id,
                changes=[entry]
            )

        # Return the updated recipe.
        data = [entry]
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Delete recipe(s).
    elif request.method == 'POST':

        # Get the existing recipe.
        ref = f'users/{uid}/recipes/{recipe_id}'
        doc = get_document(ref)

        # Delete the recipe image.
        _, project_id = google.auth.default()
        bucket_name = f'{project_id}.appspot.com'
        delete_file(doc['image_ref'], bucket_name=bucket_name)

        # Delete the recipe.
        delete_document(ref)
        
        # Return a success message.
        response = {'success': True, 'data': None}
        return Response(response, status=200)
