# Leaf

## Usage

```py
from cannlytics.traceability import leaf

trace = leaf.authorize(api_key='xyz', mme_code='abc')
lab_result = trace.create_lab_result(data)
print(lab_result.summary())
```

## Inspiration

- [Gspread](https://github.com/burnash/gspread/blob/master/gspread/models.py)
- [Spotipy](https://github.com/plamere/spotipy/blob/master/spotipy/client.py)
- [Pythentic Jobs](https://github.com/ryanmcgrath/pythentic_jobs/blob/master/pythentic_jobs.py)

::: cannlytics.traceability.leaf
    rendering:
      show_root_toc_entry: true
      show_root_heading: true
      show_source: true

<!-- ## Models

### Areas

type (str): Areas with a 'quarantine' designation are for circumstances
such as waste/destruction hold periods, QA quarantine periods,
or transfer hold periods as the licensee decides to use them.
    Allowed values:
        'quarantine' or 'non-quarantine'.

### Batches

'Propagation Material' batches are used to create inventory lot of
seeds, clones, and plant tissue so that these plants can be tracked 
as inventory throughout their propagation phase. As plants shift from
their propagation to vegetative phase, they are moved to 
plants (see /move_inventory_to_plants API call), at which point the
plant records are associated with a 'plant' type batch.

'Plant' batches are a group of plants from the same strain, that are
growing together within their vegetative and flowering phases. 
Attributes of all of the plants within a batch can be modified at the
batch level, which will apply changes across all of the plant 
records. Additionally, plant records can be modified individually
(see the /plants endpoint).

'Harvest' batches represent a group of harvested material that is all
of the same strain. These types of batches are used to denote 
both 'wet' and 'dry' weight of 'flower' and 'other material' produced
during the harvest. Resultant dry weight from a harvest batch is 
separated into 'inventory lots'. While initial inventory in a harvest
stage can be created at the 'batch' endpoint, in a general workflow 
they are made by using the /harvest_plants API call.

'Intermediate/ end product' batches are batches that consist of multiple
harvest batches being combined, for example, combining 
two different strains to make a blended concentrate product.

The purpose of using batches to group together plant and inventory
records is two-fold. Batches assist with creating the traceability 
that the system is designed to offer. As well, batches allow producers
to manage plants in any phase in groups, which enables mass 
actions to be applied to numerous records simultaneously.
Batches are not intended to constrain activities involving plant 
movement, as plants can be shifted from one batch to another and
do not have exclusive relationships with batches they are added to.

    harvest_stage (str): the stage of the harvest process;
        only used for batches with type 'harvest'.
        Allowed values:
            'wet', 'cure', 'finished'

    origin (str): Indicates propagation source of the batch.
        Required if type='plant' or 'propagation material'.
        Allowed values:
            'seed', 'clone', 'plant', 'tissue'
    
    plant_stage (str): Current development stage of the plants in 
        the batch.
        Allowed values:
            'propagation source', 'growing', 
            'harvested', 'packaged', 'destroyed'
    
    type (str): Indicates the type of batch.
        Allowed values:
            'propagation material', 'plant', 'harvest', 
            'intermediate/ end product'

### Disposals

Disposal records (referred to as "Destructions" within the UI) are
    inventory lots of waste that are created so that they can be 
    segregated from other inventory to undergo their 72-hour hold process.
    Once this time period has elapsed, physical destruction of 
    the lots may be performed. This can be accomplished through the "dispose_item" API call.
    Disposal records can be created from harvest batches (any waste associated with a harvest batch),
    inventory lots, or recorded as daily plant waste." -->
