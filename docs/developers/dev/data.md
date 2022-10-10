# Data Wrangling for Cannlytics Developers

The following documentation is intended for Cannlytics Data Scientists who wish to use or publish datasets on Hugging Face. The documentation covers:

- [Cloning a Dataset](#cloning)
- [Dataset Components](#components)
- [Publishing Datasets on Hugging Face](#publishing)
- [Testing a Dataset](#testing)

## Cloning a Dataset <a name="cloning"></a>

Install [Git Large File Storage (LFS)](https://git-lfs.github.com/) and clone your repository, for example `cannabis_tests`:

```
# Make sure that you have git-lfs installed.
git lfs install

git clone https://huggingface.co/datasets/cannlytics/cannabis_tests
```

## Dataset Components <a name="components"></a>

A dataset is composed of:

1. A `README.md` describing the dataset's contents. You can see a [template](https://raw.githubusercontent.com/huggingface/datasets/main/templates/README.md) or [read more about dataset cards](https://huggingface.co/docs/datasets/dataset_card).

2. Your data, either:
    - A `.csv` file and / or a `.json` file for your data.
    - URLs to your `.csv` and / or `.json` file(s).

    Note that it is helpful to split your dataset into training and test datafiles.

3. An optional loading script, `your_new_dataset.py`.

## Publishing Datasets on Hugging Face <a name="publishing"></a>

1. First you will want to create your dataset repository. Make sure that you are in the virtual environment where you have installed Hugging Face's `datasets` package, then run the following command to login using your Hugging Face Hub credentials:

    ```
    huggingface-cli login
    ```

    Then you can create a new dataset repository:

    ```
    huggingface-cli repo create your_new_dataset --type dataset --organization cannlytics
    ```

2. Second, you can create your metadata file, `dataset_infos.json`, and test your new dataset loading script with:

    ```
    datasets-cli test path/to/<your-dataset-folder> --save_infos --all_configs
    ```

3. Finally, you can [upload your data files](https://huggingface.co/docs/datasets/share#upload-your-files) through the Hugging Face user interface, commit through VS Code, or commit with the command line:

    ```
    cp /datasets/your_new_dataset/*.json .
    git lfs track *.json
    git add .gitattributes
    git add *.json
    git commit -m "add json files"
    cp /datasets/your_new_dataset/dataset_infos.json .
    cp /datasets/your_new_dataset/load_script.py .
    git add --all
    git status
    git commit -m "First version of the your_new_dataset dataset."
    git push
    ```

## Making a Dataset Pull Request

When you want to make a pull request to a specific dataset, first, create a pull request branch on [Hugging Face](huggingface.co), then checkout the branch:

```bash
git fetch origin refs/pr/2:pr/2
git checkout pr/2
```

Next, do your modifications and track all of your changes, including any large data files, e.g. `.csv` files:

```bash
git lfs track *.csv
git add *.csv
git commit -m "Added `csv` files"
git add --all
git status
git commit -m "Updated `cannabis_licenses` dataset."
git push
```

Finally, make the pull request:

```bash
git push origin pr/2:refs/pr/2
```

🎉 Congratulations, your pull request is now ready to be reviewed and merged by the repository admin!

## Testing a Dataset <a name="testing"></a>

You can create dummy data for te dataset with:

```
datasets-cli dummy_data datasets/<your-dataset-folder> --auto_generate
```

You can also load the dataset locally in Python, for example:

```py
from datasets import load_dataset

# Load the dataset.
dataset = load_dataset('cannabis_licenses.py', 'ca')
data = dataset['data']
assert len(data) > 0
print('Read %i data points.' % len(data))
```
