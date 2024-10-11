"""
Models
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/9/2024
Updated: 9/29/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from typing import List, Optional

# External imports:
from pydantic import BaseModel, Field, HttpUrl


class DataSource(BaseModel):
    """A reference or source of information."""
    title: str
    url: HttpUrl


class ProductImage(BaseModel):
    """An image associated with an entity."""
    url: HttpUrl
    filename: Optional[str] = None
    caption: Optional[str] = None


class License(BaseModel):
    """A licensed cannabis company."""
    id: str = Field(..., description="A state-unique ID for the license.")
    license_number: str = Field(..., description="A unique license number.")
    status: Optional[str] = Field(..., description="The status of the license. Only licenses that are active are included.")
    type: Optional[str] = Field(..., description="The type of business license.")
    issue_date: Optional[str] = Field(None, description="An ISO-formatted issue date for the license.")
    expiration_date: Optional[str] = Field(None, description="An ISO-formatted expiration date for the license.")
    legal_name: str = Field(..., description="The legal name of the business that owns the license.")
    dba: Optional[str] = Field(None, description="The name the license is doing business as.")
    owner_name: Optional[str] = Field(None, description="The name of the owner of the license.")
    address: Optional[str] = Field(..., description="The street address of the business.")
    city: Optional[str] = Field(..., description="The city of the business.")
    state: Optional[str] = Field(..., description="The state abbreviation of the business.")
    county: Optional[str] = Field(None, description="The county of the business.")
    zip_code: Optional[str] = Field(..., description="The zip code of the business.")
    email: Optional[str] = Field(None, description="The business email of the license.")
    phone: Optional[str] = Field(None, description="The business phone of the license.")
    website: Optional[HttpUrl] = Field(None, description="The business website of the license.")
    latitude: Optional[float] = Field(None, description="The latitude of the business.")
    longitude: Optional[float] = Field(None, description="The longitude of the business.")
    updated_at: Optional[str] = Field(None, description="An ISO-formatted time when the license data was updated.")


class Strain(BaseModel):
    """A cannabis strain."""
    strain_id: str = Field(..., description="A unique identifier for the strain.")
    strain_name: str = Field(..., description="The name of the strain.")
    origin_state: Optional[str] = Field(None, description="The origin of the strain.")
    first_date_tested: Optional[str] = Field(None, description="The first time the strain was tested, ISO-format.")
    image_url: Optional[HttpUrl] = Field(None, description="URL to the main image of the strain.")
    images: Optional[List[ProductImage]] = Field(None, description="A list of image URLs related to the strain.")
    aliases: Optional[List[str]] = Field(None, description="Known aliases or other names for the strain.")
    breeder: Optional[str] = Field(None, description="The breeder or creator of the strain.")
    chemotype: Optional[str] = Field(None, description="The chemotype classification of the strain.")
    female_parent: Optional[str] = Field(None, description="The female parent of the strain.")
    male_parent: Optional[str] = Field(None, description="The male parent of the strain.")
    children: Optional[List[str]] = Field(None, description="Strains that are children of the strain.")
    indica_percentage: Optional[float] = Field(None, description="Estimated percentage of Indica genetics.")
    sativa_percentage: Optional[float] = Field(None, description="Estimated percentage of Sativa genetics.")
    description: Optional[str] = Field(None, description="Description of the strain.")
    folklore: Optional[str] = Field(None, description="Folklore or stories associated with the strain.")
    etymology: Optional[str] = Field(None, description="The etymology or origin of the strain's name.")
    history: Optional[str] = Field(None, description="History of the strain.")
    references: Optional[List[DataSource]] = Field(None, description="References or sources for information about the strain.")
    avg_total_thc: Optional[float] = Field(None, description="Average total THC concentration observed.")
    avg_total_cbd: Optional[float] = Field(None, description="Average total CBD concentration observed.")
    avg_price_per_gram: Optional[float] = Field(None, description="Average price per gram.")
    created_at: Optional[str] = Field(None, description="The creation date of the strain entry, ISO-format.")
    updated_at: Optional[str] = Field(None, description="The last update date of the strain entry, ISO-format.")


class Product(BaseModel):
    """A cannabis product."""
    batch_number: Optional[str] = Field(None, description="The batch number of the product.")
    distributor: Optional[str] = Field(None, description="The distributor of the product.")
    distributor_license_number: Optional[str] = Field(None, description="The distributor's license number.")
    images: Optional[List[ProductImage]] = Field(None, description="Images of the product.")
    producer: Optional[str] = Field(None, description="The producer of the product.")
    producer_license_number: Optional[str] = Field(None, description="The producer's license number.")
    product_id: str = Field(..., description="The unique identifier for the product.")
    product_name: str = Field(..., description="The name of the product.")
    product_size: Optional[float] = Field(None, description="The size of the product in milligrams.")
    product_type: str = Field(..., description="The type of the product.")
    product_weight: Optional[float] = Field(None, description="The weight of the product.")
    retailer: Optional[str] = Field(None, description="The retailer of the product.")
    retailer_license_number: Optional[str] = Field(None, description="The retailer's license number.")
    sample_ids: Optional[List[str]] = Field(None, description="A list of sample IDs associated with the product.")
    strain_ids: Optional[List[str]] = Field(None, description="A list of strain IDs associated with the product.")
    strain_name: Optional[str] = Field(None, description="The strain name associated with the product.")
    total_cannabinoids: Optional[float] = Field(None, description="The total cannabinoids content of the product.")
    total_cbd: Optional[float] = Field(None, description="The total CBD content of the product.")
    total_terpenes: Optional[float] = Field(None, description="The total terpene content of the product.")
    total_thc: Optional[float] = Field(None, description="The total THC content of the product.")


class LabelResult(BaseModel):
    """A lab test result found on a cannabis product label."""
    name: str = Field(..., description="The name of the analyte tested.")
    percentage: float = Field(..., description="The percentage of the analyte found in the product.")


class Label(BaseModel):
    """A label for a cannabis product."""
    batch_number: str = Field(..., description="The batch number of the product.")
    cannabinoids_units: str = Field(..., description="The units used to measure cannabinoid content.")
    date_packaged: str = Field(..., description="The ISO-formatted date when the product was packaged.")
    results: list[LabelResult] = Field(..., description="A list of lab test results found on the label.")
    lineage: str = Field(..., description="The lineage or genetic background of the cannabis strain.")
    price: float = Field(..., description="The price of the product.")
    producer: str = Field(..., description="The name of the producer or manufacturer.")
    producer_state: str = Field(..., description="The state where the producer is located.")
    product_name: str = Field(..., description="The name of the cannabis product.")
    product_type: str = Field(..., description="The type or category of the product (e.g., flower, concentrate).")
    product_weight: float = Field(..., description="The weight of the product, typically in grams.")
    product_id: str = Field(..., description="A unique identifier for the product.")
    strain_name: str = Field(..., description="The name of the cannabis strain used in the product.")
    strain_type: str = Field(..., description="The type of cannabis strain (e.g., Indica, Sativa, Hybrid).")
    terpenes_units: str = Field(..., description="The units used to measure terpene content.")
    total_cbd: float = Field(..., description="The total percentage of CBD in the product.")
    total_terpenes: float = Field(..., description="The total percentage of terpenes in the product.")
    total_thc: float = Field(..., description="The total percentage of THC in the product.")


class Result(BaseModel):
    """A lab result analyte measurement."""
    analysis: str = Field(..., description="The analysis used to obtain the result.")
    key: str = Field(..., description="A standardized key for the result analyte.")
    name: str = Field(..., description="The lab's internal name for the result analyte.")
    value: Optional[float] = Field(None, description="The value of the result.")
    units: Optional[str] = Field(None, description="The units for the result value, limit, LOD, and LOQ.")
    limit: Optional[float] = Field(None, description="A pass/fail threshold for contaminant screening analyses.")
    status: Optional[str] = Field(None, description="The pass/fail status for contaminant screening analyses.")
    lod: Optional[float] = Field(None, description="The limit of detection for the analyte.")
    loq: Optional[float] = Field(None, description="The limit of quantification for the analyte.")
    mg_g: Optional[float] = Field(None, description="The value of the result in milligrams per gram.")


class LabResult(BaseModel):
    """A lab result for a cannabis product sample."""
    analyses: Optional[List[str]] = Field([], description="A list of analyses performed on the sample.")
    methods: Optional[dict] = Field(None, description='Methods used for each analysis. E.g. [{"analysis": "cannabinoids", "method": "HPLC"}]')
    statuses: Optional[dict] = Field(None, description='The pass/fail status for each pass/fail analysis. E.g. [{"analysis": "pesticides", "status": "pass"}]')
    batch_number: Optional[str] = Field(None, description="A batch number for the sample or product.")
    coa_url: str = Field(None, description="A URL to the certificate of analysis (COA), typically a PDF.")
    date_harvested: Optional[str] = Field(None, description="An ISO-formatted time when the sample was harvested.")
    date_collected: Optional[str] = Field(None, description="An ISO-formatted time when the sample was collected.")
    date_received: Optional[str] = Field(None, description="An ISO-formatted time when the sample was received.")
    date_tested: Optional[str] = Field(None, description="An ISO-formatted time when the sample was tested.")
    distributor: Optional[str] = Field(None, description="The name of any product distributor, if applicable.")
    distributor_address: Optional[str] = Field(None, description="The distributor's address, if applicable.")
    distributor_city: Optional[str] = Field(None, description="The distributor's city, if applicable.")
    distributor_license_number: Optional[str] = Field(None, description="The distributor's license number, if applicable.")
    distributor_state: Optional[str] = Field(None, description="The distributor's state, if applicable.")
    distributor_zipcode: Optional[str] = Field(None, description="The distributor's zip code, if applicable.")
    image_url: str = Field(None, description="A URL to an image of the product sample.")
    lab_id: Optional[str] = Field(None, description="A lab-specific ID for the sample.")
    lab: Optional[str] = Field(None, description="The name of the lab that tested the sample.")
    lab_license_number: Optional[str] = Field(None, description="The lab's license number.")
    lab_address: Optional[str] = Field(None, description="The lab's address.")
    lab_city: Optional[str] = Field(None, description="The lab's city.")
    lab_state: Optional[str] = Field(None, description="The lab's state.")
    lab_zipcode: Optional[str] = Field(None, description="The lab's zip code.")
    producer: Optional[str] = Field(None, description="The producer of the sampled product.")
    producer_address: Optional[str] = Field(None, description="The producer's address.")
    producer_city: Optional[str] = Field(None, description="The producer's city.")
    producer_license_number: Optional[str] = Field(None, description="The producer's license number.")
    producer_state: Optional[str] = Field(None, description="The producer's state.")
    producer_zipcode: Optional[str] = Field(None, description="The producer's zip code.")
    product_name: Optional[str] = Field(None, description="The name of the product.")
    product_size: Optional[float] = Field(None, description="The size of the product in milligrams.")
    product_type: Optional[str] = Field(None, description="The type of product.")
    results: List[Result] = Field([], description="A list of results.")
    results_url: Optional[HttpUrl] = Field(None, description="A URL to the results displayed online (not necessarily a COA).")
    results_hash: Optional[str] = Field(None, description="An HMAC of the sample's results JSON signed with Cannlytics' public key.")
    sample_hash: Optional[str] = Field(None, description="An HMAC of the entire sample JSON signed with Cannlytics' public key.")
    sample_id: Optional[str] = Field(None, description="A generated ID to uniquely identify the sample.")
    sample_weight: Optional[float] = Field(None, description="The weight of the lab sample in grams.")
    serving_size: Optional[float] = Field(None, description="An estimated serving size in milligrams.")
    servings_per_package: Optional[int] = Field(None, description="The number of servings per package.")
    status: Optional[str] = Field(None, description="The overall pass/fail status for all contaminant screenings.")
    strain_name: Optional[str] = Field(None, description="A strain name, if specified.")
    strain_type: Optional[str] = Field(None, description="The type of strain, if specified. E.g. Indica, Sativa, Hybrid.")
    total_cannabinoids: Optional[float] = Field(None, description="The total cannabinoids measured.")
    total_cbd: Optional[float] = Field(None, description="The total CBD content.")
    total_thc: Optional[float] = Field(None, description="The total THC content.")
    total_terpenes: Optional[float] = Field(None, description="The sum of all terpenes measured.")
    traceability_ids: Optional[List[str]] = Field(None, description="A list of traceability IDs.")


class SalesItem(BaseModel):
    """An item purchased in a transaction."""
    product_name: str = Field(..., description="The name of the product purchased.")
    strain_name: Optional[str] = Field(None, description="The strain name of the product.")
    product_type: str = Field(..., description="The type of the product purchased.")
    quantity: float = Field(..., description="The quantity of the product purchased.")
    weight: Optional[float] = Field(None, description="The weight of the product purchased.")
    price: float = Field(..., description="The price of the product purchased.")
    product_id: str = Field(..., description="The ID of the product purchased.")


class Receipt(BaseModel):
    """A receipt for a cannabis transaction."""
    date_sold: str = Field(..., description="The date the receipt was sold, ISO-format.")
    invoice_number: str = Field(..., description="The receipt number.")
    items: List[SalesItem] = Field(..., description="A list of purchased items.")
    total_amount: float = Field(..., description="The total amount of all product prices.")
    subtotal: float = Field(..., description="The subtotal of the receipt.")
    total_discount: Optional[float] = Field(0.0, description="The amount of discount applied, if applicable.")
    total_paid: float = Field(..., description="The total amount paid.")
    change_due: Optional[float] = Field(0.0, description="The amount of change due.")
    rewards_earned: Optional[float] = Field(0.0, description="The amount of rewards earned.")
    rewards_spent: Optional[float] = Field(0.0, description="The amount of rewards spent.")
    total_rewards: Optional[float] = Field(0.0, description="The total amount of rewards.")
    city_tax: Optional[float] = Field(0.0, description="The amount of city tax applied.")
    county_tax: Optional[float] = Field(0.0, description="The amount of county tax applied.")
    state_tax: Optional[float] = Field(0.0, description="The amount of state tax applied.")
    excise_tax: Optional[float] = Field(0.0, description="The amount of excise tax applied.")
    retailer: str = Field(..., description="The name of the retailer.")
    retailer_license_number: str = Field(..., description="The license number of the retailer.")
    retailer_address: str = Field(..., description="The address of the retailer.")
    retailer_street: Optional[str] = Field(None, description="The retailer's street, if applicable.")
    retailer_city: Optional[str] = Field(None, description="The retailer's city, if applicable.")
    retailer_state: Optional[str] = Field(None, description="The retailer's state, if applicable.")
    retailer_zipcode: Optional[str] = Field(None, description="The retailer's zip code, if applicable.")
    budtender: Optional[str] = Field(None, description="The name of the budtender.")
    product_ids: Optional[List[str]] = Field(None, description="A list of product IDs associated with the receipt.")
    sample_ids: Optional[List[str]] = Field(None, description="A list of sample IDs associated with the receipt.")


class Comment(BaseModel):
    """A comment on a review."""
    comment_id: str = Field(..., description="The unique identifier for the comment.")
    comment_author: str = Field(..., description="The username of the comment's author.")
    comment_body: str = Field(..., description="The body content of the comment.")
    comment_created_at: str = Field(..., description="The date and time the comment was created, ISO-format.")


class ReportedEffect(BaseModel):
    """An effect reported in a review."""
    effect: str = Field(..., description="The reported effect.")
    positive: bool = Field(..., description="Indicates if the effect was positive.")
    rating: int = Field(..., description="A rating for the effect, typically from 1 to 10.")


class ReportedAroma(BaseModel):
    """An aroma reported in a review."""
    aroma: str = Field(..., description="The reported aroma.")
    positive: bool = Field(..., description="Indicates if the aroma was positive.")
    rating: int = Field(..., description="A rating for the aroma, typically from 1 to 10.")


class Review(BaseModel):
    """A review of a cannabis product or strain."""
    post_id: str = Field(..., description="The unique identifier for the review.")
    post_url: HttpUrl = Field(..., description="The URL of the review.")
    title: str = Field(..., description="The title of the review.")
    post_content: str = Field(..., description="The body of the review.")
    created_at: str = Field(..., description="The date and time the review was created, ISO-format.")
    author: str = Field(..., description="The username of the author.")
    author_id: str = Field(..., description="The unique identifier for the author.")
    upvotes: int = Field(..., description="The number of upvotes the review has received.")
    downvotes: int = Field(..., description="The number of downvotes the review has received.")
    number_comments: int = Field(..., description="The number of comments the review has received.")
    comments: Optional[List[Comment]] = Field(None, description="A list of comments on the review.")
    reported_effects: Optional[List[ReportedEffect]] = Field(None, description="A list of reported effects from the review.")
    reported_aromas: Optional[List[ReportedAroma]] = Field(None, description="A list of reported aromas from the review.")
    product_ids: Optional[List[str]] = Field(None, description="A list of product IDs associated with the review.")
    sample_ids: Optional[List[str]] = Field(None, description="A list of sample IDs associated with the review.")
