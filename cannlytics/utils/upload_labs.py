# -*- coding: utf-8 -*-
"""
Upload Labs | Cannlytics
Copyright © 2021 Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 1/12/2021

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""
import os
import pandas as pd
from django.template.defaultfilters import slugify
from firebase_admin import initialize_app, firestore
from uuid import uuid4


def upload_labs(input_file, sheet_name="All Labs"):
    """Upload lab data points to Firestore."""
    try:
        initialize_app()
    except ValueError:
        pass
    database = firestore.client()
    collection = database.collection("labs")
    labs = pd.read_excel(
        input_file,
        sheet_name=sheet_name,
        converters={
            "license_expiration_date": str,
            "license_issue_date": str,
        },
    )
    labs = labs.where(pd.notnull(labs), None)
    for index, row in labs.iterrows():
        _id = str(uuid4())
        docs = collection.where(u"license", u"==", row.license).stream()
        for doc in docs:
            _id = doc.id
        values = row.to_dict()
        values["id"] = _id
        values["slug"] = slugify(values["name"])
        collection.document(_id).set(values, merge=True)
        print("Uploaded lab data for:", row["name"])


if __name__ == "__main__":

    upload_labs(input_file="./data/All Labs.xlsx", sheet_name="All Labs")
