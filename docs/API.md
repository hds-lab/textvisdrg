API Documentation
=================

The primary function of the API is to provide access to statistical summaries
of the message database that can be used to render visualizations.
With many of the API requests, a JSON object should be provided that
indicates the user’s current interest and affects how the results will be delivered.

Below are links to the main API data objects:

- [Dimensions](#dimensions)
- [Filters](#filters)
- [Messages](#messages)
- [Questions](#questions)
- Snapshots
- Message Contexts

The table below summarizes the API endpoints:

| Endpoint                                  | Url             | Purpose                                         |
| ----------------------------------------- | --------------- | ----------------------------------------------- |
| [Data Table](#data-table)                 | /api/table      | Get table of counts based on dimensions/filters |
| [Example Messages](#example-messages)     | /api/messages   | Get example messages for slice of data          |
| [Research Questions](#research-questions) | /api/questions  | Get RQs related to dimensions/filters           |
| [Describe Dimension](#describe-dimension) | /api/dimension  | Get distribution of a dimension                 |
| [Describe Filter](#describe-filter)       | /api/filter     | Get info about behavior of filter               |
| Message Context                           | /api/context    | Get context for a message                       |
| Snapshots                                 | /api/snapshots  | Save a visualization snapshot                   |


API Objects
-----------

This section explains and gives examples of the main API data objects,
some of which are used across multiple API endpoints.


### Dimensions

Dimension objects describe the variables that users
can select to visualize the dataset. An example is below:

```json
{
  "id": 5
  "name": "time",
  "description": "the time the message was sent",
  "scope": "open",
  "type": "quantitative",
}
```


### Filters

Filters indicate a subset of the range of a specific dimension.
Below is an array of three filter objects.

```json
[{
  "dimension": 5,
  "min": "2010-02-25T00:23:53Z",
  "max": "2010-02-30T00:23:53Z"
},
{
  "dimension": 2,
  "include": [
    "cat",
    "dog",
    "alligator"
  ]
},
{
  "dimension": 6,
  "max": 100
}]
```

Although every filter has a `dimension` field,
the specific properties vary depending on the type of
the dimension and the kind of filter.

At this time, there are two types of filters:

- Quantitative dimensions can be filtered using one or both
  of the `min` and `max` properties (inclusive).
- Categorical dimensions can be filtered by specifying
  an `include` list. All other items are assumed to be excluded.


### Messages

Messages are provided in a simple format
that is useful for displaying examples:

```json
{
  "id": 52,
  "text": "Some sort of thing or other",
  "sender": "A name",
  "time": "2010-02-25T00:23:53Z"
}
```

Additional fields may be added later.


### Questions

Research questions extracted from papers
are given in the following format:

```json
{
  "id": 5,
  "text": "What is your name?",
  "source": {
    "id": 13,
    "authors": "Thingummy & Bob",
    "link": "http://ijn.com/3453295",
    "title": "Names and such",
    "year": "2001",
    "venue": "International Journal of Names"
  },
  "dimensions": [
    "time",
    "user"
  ]
}
```

The `source` object describes a research article reference
where the question originated.

The `dimensions` list indicates which dimensions the
research question is associated with.


API Endpoints
-------------

Below are the API endpoints.


### Data Table

Get a table of message counts or other statistics based on
the current dimensions and filters.

The request should post a JSON object containing a list
of one or two dimension ids and a list of filters.
A `measure` may also be specified in the request, but
the default measure is message count.

The response will be a JSON object that mimics the request body,
but with a new `result` field added, which will be a list of objects.

Each object in the result field represents a cell in a table
or a dot (for scatterplot-type results). For every dimension
in the dimensions list (from the request), the result object will include
a property keyed to the name of the dimension and a value for that dimension.
A `value` field provides the requested summary statistic.

This is the most general output format for results,
but later we may switch to a more compact format.

**Request:** `POST /api/table`

**Example Request Body:**

```json
{
  "dimensions": [5, 8],
  "filters": [
    {
      "dimension": 5,
      "min": "2010-02-25T00:23:53Z",
      "max": "2010-02-30T00:23:53Z"
    }
  ],
  "measure": {
    "statistic": "message",
    "aggregation": "count"
  }
}
```

**Example Response Body:**

```json
{
  "dimensions": [5, 8],
  "filters": [
    {
      "dimension": 5,
      "min": "2010-02-25T00:23:53Z",
      "max": "2010-02-30T00:23:53Z"
    }
  ],
  "result": [
    {
      "value": 35,
      "time": "2010-02-25T00:23:53Z"
    },
    {
      "value": 35,
      "time": "2010-02-26T00:23:53Z"
    },
    {
      "value": 35,
      "time": "2010-02-27T00:23:53Z"
    },
    {
      "value": 35,
      "time": "2010-02-28T00:23:53Z"
    }
  ]
}
```


### Example Messages

Get some example messages matching the current filters
and a focus within the visualization.

The request should include a list of dimension ids
and active filters. It should also include a `focus` object
that specifies values for one or both of the given dimensions,
keyed by name.

The response will be a list of [message objects](#messages).

**Request:** `POST /api/messages`

**Example Request Body:**

```json
{
  "dimensions": [5, 8],
  "filters": [
    {
      "dimension": 5,
      "min": "2010-02-25T00:23:53Z",
      "max": "2010-02-30T00:23:53Z"
    }
  ],
  "focus": {
    "time": "2010-02-30T00:23:53Z"
  }
}
```


### Research Questions

Get a list of research questions related to a selection
of dimensions and filters.

The request should include a list of dimension ids
and active filters.

The response will be a list of [research questions](#research-questions).

**Request:** `POST /api/questions`

**Example Request Body:**

```json
{
  "dimensions": [5, 8],
  "filters": [
    {
      "dimension": 5,
      "min": "2010-02-25T00:23:53Z",
      "max": "2010-02-30T00:23:53Z"
    }
  ]
}
```


### Describe Dimension

In order to display helpful information for filtering,
the distribution of a dimension may be queried using this API endpoint.

The request should include a dimension `id` and an optional `query`
for very large dimensions that support filtering the distribution.

The response will include a `domain` property that is a list
of values for the dimension with a message count at each value.

**Request:** `POST /api/dimension`

**Example Request Body:**

```json
{
  "id": 7,
  "query": "cat"
}
```

**Example Response:**

```json
{
  "id": 7,
  "query": "cat",
  "domain": [
    {
      "count": 5000,
      "value": "cat"
    },
    {
      "count": 1000,
      "value": "catch"
    },
    {
      "count": 500,
      "value": "cathedral"
    },
    {
      "count": 50,
      "value": "cataleptic"
    }
  ]
}
```


### Describe Filter

When a filter is being used, it is useful to know information
about how the filter behaves on the dataset.

The request should include a [filter object](#filters).

The response will add a `summary` object
that includes some statistics about the filter.

**Request:** `POST /api/filter`

**Example Request Body:**

```json
{
  "dimension": 5,
  "min": "2010-02-25T00:23:53Z",
  "max": "2010-02-30T00:23:53Z"
}
```

**Example Response:**

```json
{
  "dimension": 5,
  "min": "2010-02-25T00:23:53Z",
  "max": "2010-02-30T00:23:53Z",
  "summary": {
    "included": 502343
  }
}
```

