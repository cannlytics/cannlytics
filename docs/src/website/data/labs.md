# Data Structures

Two of the primary model objects of the Cannlytics engine are `organizations` and `users`. An `organization`, designated by a unique `org_id`, with `type` equal to `"lab"` is a cannabis testing laboratory and an organizations with `type` equal to `"client"` is a laboratory client. Organizations have an array of users, who each have unique `user_id`'s. Users can add organizations if they do not exist, becoming the owner of the organization. Only organization owners can add users to the organization's team.

## Organizations

Labs are encouraged to make as many organizations as they need. A small lab may like to create a *production* organization and a *dev* organization to separate their live environment from the environment where they can conduct internal software quality assurance testing. Larger labs may like to create organizations for each branch or facility that they may operate. Owners of organizations can add other users to the organization, with the receiving user being added to the `organizations/{org_id}`'s `team` field. For example:

```js
`organizations/{org_id}`: {
    team: [{user_id_1}, {user_id_2}, {user_id_3} ...]
    .
    .
    .
}
```

All of a lab's clients are given a unique organization ID and document in `organizations/{org_id}`. The client's organization data structure is similar to the data structure of a lab, except the client has `type` equal to `client` by default, which will alter the user's Cannlytics console to display sections that clients can use to browse and analyze their lab results. Labs, organizations with `type` equal to `lab`, can view the Cannlytics console as if they were a `client` as well.

It is not necessary for clients to create their own organization accounts to receive links to their results, but all are welcome to create and use an organization account to manage their team and lab results and interact with other organizations, such as sharing their lab results. When a lab adds a client, if the organization does not yet exist, then an organization is created and the client is invited to become the owner. User accounts are also created for each of the client's contacts. As a part of an organization, the client has easy access to all of their results from all labs integrated with the Cannlytics engine. Like labs, client users can create any number of organizations. The default schema of an `organization` is as follows.

```js
`organizations/{org_id}` = {
    analyses: String,
    city: String,
    county: String,
    current_lims: String,
    email: String,
    feedback: String,
    image_url: String,
    interested_in_new_lims: String,
    latitude: Number,
    license: String,
    linkedin: String,
    longitude: Number,
    name: String,
    owner: String, // Owner's {user_id}
    phone: String,
    state: String,
    status: String,
    street: String,
    team: Array, // Array of {user_id}'s
    trade_name: String,
    top_problems: Array,
    type: String,
    twitter: String,
    website: String,
    zip: String,
}
```

Each organization document, `organizations/{org_id}/`, has the following subcollections.

- `admin/{keychain_id}`
- `analyses/{analysis_id}`
- `batches/{batch_id}`
- `calculations/{calculation_id}`
- `calendar/{iso_date}`
- `clients/{org_id}`
- `coas/{sample_id}`
- `files/{file_id}`
- `instruments/{instrument_id}`
- `inventory/{inventory_id}`
- `invoices/{invoice_id}`
- `logs/{iso_time}`
- `measurements/{measurement_id}`
- `notifications/{iso_time}`
- `projects/{project_id}`
- `reports/{report_id}`
- `results/{sample_id}`
- `samples/{sample_id}`
- `stats/{stat_id}`
- `templates/{template_id}`
- `transfers/{transfer_id}`

Each subcollection is explained in the corresponding section in the documentation.

## Users

Users can read the documents of any organization that they are part of, designated by organization documents where the `team` field includes their `user_id`. Users can write to any subcollection authorized by the organization owner. Only an organization owner can write to the organization document. On organization creation, the creating user gets a custom claim `owner`, which is an array that contains the `org_id`. For example:

```js
{ owner: [{org_id_1}, {org_id_2}, {org_id_3} ...]
```

Writes are only permitted to `organizations/{org_id}` if the user has custom claim `owner` with the `org_id`. Reads are permitted if a user's `user_id` is in the `organizations/{org_id}`'s `team` field, which is an array of all users' `{user_id}` that are members of the organization. The default schema of a `user` is as follows.

```js
`users/{user_id}`: {
  name: String,
  email: String,
  phone: String,
  photo_url: String,
  position: String,
  website: String,
  location: String,
  organizations: Array,
  support: String, // "free", "pro", "enterprise"
}
```

Each user document has the following subcollections:

- `users/{user_id}/feedback/{id}`
- `users/{user_id}/logs/{id}`

Data in these subcollections is explained in the following documentation.
