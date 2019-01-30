# Public Transit Referential grammar

It's possible to do advanced query to the public transit referential. The query is in the form `/v1/coverage/id/collections?filter=query`. This is the documentation of the `query` syntax. For simplicity, the queries in this documentation will not be urlencoded, but it must be in practice.

Each query is composed of 2 parts: the collection to be asked (`collections` in the example), and the query itself that describe the wanted objects.

The valid collections are `commercial_modes`, `companies`, `connections`, `contributors`, `datasets`, `disruptions`, `journey_patterns`, `journey_pattern_points`, `lines`, `networks`, `physical_modes`, `poi_types`, `pois`, `routes`, `stop_areas`, `stop_points` and `vehicle_journeys`.

The `traffic_reports` endpoint builds its response on the `networks` collection.

The `line_reports` endpoint builds its response on the `lines` collection.

The `route_schedules` endpoint builds its response on the `routes` collections.

The `arrivals`, `departures` and `stop_schedules` endpoint builds their responses on the `journey_pattern_points` collection.

## Predicates

The elementary building block of a query is the predicate. They define a set of requested objects.

### Elementary predicates

There is 2 elementary predicates: `all` and `empty`. As expected, `all` returns all the queried objects while `empty` returns none.

Examples:
 * `/v1/coverage/id/stop_areas?filter=all`: returns all the stop areas of the coverage.
 * `/v1/coverage/id/stop_areas?filter=none`: returns 0 stop areas (you get a 404).
 
### Method predicates

Method predicates are in the form `collection.method(string, string, ...)` where:
 * `collection` is a collection name (as the collections queried, but singular);
 * `method` is a method name, corresponding to the filter on the `collection`;
 * arguments to the method between `(` and `)`, as strings, separated by `,`.
 
#### Strings
 
A string can be:
 * an escaped string, begining and ending with `"`, with `\x` transformed as `x` within the string
 * a basic string, composed of any letter, digit, `_`, `.`, `:`, `;`, `|` and `-`.
 
Basic strings are great to easily type numbers and navitia coordinates. It can also handle most of the identifiers, but be warned that you will run into troubles if you use the basic string syntax in a programatic way (think of identifiers with spaces or accentuated letters).

For programatic usage, it is recommended to:
 * substitute `"` by `\"` and `\` by `\\`
 * surround the string with `"`

Examples:
 * `1337`
 * `-42`
 * `-123.45e-12`
 * `2.37715;48.846781`
 * `"I can have spaces and accentuated letters: éèà"` (decoded as `2.37715;48.846781`)
 * `"a \" and a \\ within a string"` (decoded as `a " and a \ within a string`)

#### Availlable methods

In the following table, if the invocation is begining with `collection`, any collection can be used, else the method will only work for the specified collection.

| query | signification | note |
|-------|---------------|------|
|`collection.has_code(type, value)`|all the objects of type `collection` that have the code `{type: "type", value: "value"}` in `codes[]`|only the `codes[]` field is used|
|`collection.id(id)`|the object of type `collection` that have `id` as identifier (empty if this identifier is not present)|for types without identifier (as `connection`), it is equivalent to `empty`|
|`collection.uri(id)`|same as `collection.id(id)`||
|`collection.name(name)`|all the objects of type `collection` that have `name` as name|for types without name (as `connection`), it is equivalent to `empty`|
|`disruption.between(since, until)`|all the disruptions that are active during the `[since, until]` period|`since` and `until` must be UTC datetime in the ISO 8601 format (ending with `Z`)|
|`disruption.since(since)`|all the disruptions that are active after the given datetime|`since` must be UTC datetime in the ISO 8601 format (ending with `Z`)|
|`disruption.tag(tag)`|all the disruptions containing the given tag|equivalent to `disruption.tags(tag)`|
|`disruption.tags(tag1, tag2, ...)`|all the disruptions containing at least one of the given tags|at least one tag must be given|
|`disruption.until(until)`|all the disruptions that are active before the given datetime|`until` must be UTC datetime in the ISO 8601 format (ending with `Z`)|
|`line.code(code)`|all the lines containing the given code|this predicate use the field `line.code`, not `line.codes[]`|
|`line.odt_level(level)`|all the lines with the given on demand transport property|level can be `scheduled`, `with_stops` or `zonal`|
|`poi.within(distance, coord)`|all the POIs within `distance` meters from `coord`|`distance` in a positive integer, `coord` is a navitia coord (`lon;lat`)|
|`stop_area.within(distance, coord)`|all the stop areas within `distance` meters from `coord`|`distance` in a positive integer, `coord` is a navitia coord (`lon;lat`)|
|`stop_point.within(distance, coord)`|all the stop points within `distance` meters from `coord`|`distance` in a positive integer, `coord` is a navitia coord (`lon;lat`)|
|`vehicle_journey.between(since, until)`|all the vehicle journeys that start during the `[since, until]` period|`since` and `until` must be UTC datetime in the ISO 8601 format (ending with `Z`)|
|`vehicle_journey.has_disruption()`|all the vehicle journeys containing at least a disruption ||
|`vehicle_journey.has_headsign(headsign)`|all the vehicle journeys containing the given headsign ||
|`vehicle_journey.since(since)`|all the vehicle journeys that start after the given datetime|`since` must be UTC datetime in the ISO 8601 format (ending with `Z`)|
|`vehicle_journey.until(until)`|all the vehicle journeys that start before the given datetime|`until` must be UTC datetime in the ISO 8601 format (ending with `Z`)|

#### Interpretation

Each predicate correspond to a set of object of a given type, but the request might be from another type. In this case, the request will return the objects corresponding to the set of objects described by the predicate.

For example, if you have the request `/v1/coverage/id/lines?filter=stop_area.name("Mairie")`, you first get the set of the stop areas with "Mairie" as name, and then returns all the lines that pass by these stop areas.

### Field test predicates

As a short hand, every method with exactly one parameter of the form `collection.method(param)` can be rewritten as `collection.method = param` (with or without spaces around `=`).

Example:
 * `stop_area.id("foo")` can be written `stop_area.id = "foo"`
 * `line.code(14)` can be written `line.code=14`

### DWITHIN predicate

For backward compatibility, `collection.within(distance, lon;lat)` can be written `collection.coord DWITHIN(lon, lat, distance)`. This syntax is deprecated and might disapear in a futur release.

## Expressions

Now, we have predicates to select object, and we need a tool to combine these predicate. Expressions are this tool. There is 3 different operators:
 * `AND` (or `and`): returns the intersection between the 2 predicates
 * `OR` (or `or`): returns the union between the 2 predicates
 * `-`: returns the set difference between the 2 predicates
 
 ### `AND`
 
 `/v1/coverage/id/collections?filter=pred1 and pred2` is equivalent to take the objects in common between `/v1/coverage/id/collections?filter=pred1` and `/v1/coverage/id/collections?filter=pred2`.
 
 Example:
 * `/v1/coverage/id/stop_areas?filter=network.id=RATP and physical_mode.id=physical_mode:Bus` returns the stop areas where buses of the network RATP stop.
 * `/v1/coverage/id/lines?filter=stop_area.name=Nation and stop_area.name="Charles de Gaulle Etoile"` returns the lines that stop at Nation and Charles de Gaulle Etoile.
 * `/v1/coverage/id/lines?filter=line.code=14 and physical_mode.id=physical_mode:Metro` returns the metro lines with code 14.
 
 ### `OR`
 
 `/v1/coverage/id/collections?filter=pred1 or pred2` is equivalent to take the objects that appear in `/v1/coverage/id/collections?filter=pred1` or in `/v1/coverage/id/collections?filter=pred2`.
 
 Examples:
 * `/v1/coverage/id/pois?filter=poi.id=foo or poi.id=bar` returns the pois `foo` and `bar` (if they exists).
 * `/v1/coverage/id/stop_areas?filter=line.code=A or line.code=B` returns the stop areas where line A or line B stop.
 * `/v1/coverage/id/lines?filter=physical_mode.id=physical_mode:Metro or network.id=SNCF` returns the SNCF lines and the Metro lines.
 
 ### `-`
 
 `/v1/coverage/id/collections?filter=pred1 - pred2` is equivalent to take the objects that appear in `/v1/coverage/id/collections?filter=pred1` and remove the objects that appear in `/v1/coverage/id/collections?filter=pred2`.
 
 Examples:
 * `/v1/coverage/id/physical_modes?filter=all - physical_mode.id=physical_mode:Bus` returns all the physical modes except Bus.
 * `/v1/coverage/id/lines?filter=network.id=SNCF - physical_mode.id=physical_mode:Bus` returns the lines from the network SNCF that don't have buses.
 * `/v1/coverage/id/lines?filter=physical_mode.id=physical_mode:Metro - stop_area.name=Nation` returns the metro lines that don't stop at Nation.
 
 ### Combining expressions
 
 You can combine operators to create more complicated expressions. The priorities of the operators are chosen to feel natural to programmers: `-`, `AND`, `OR` is the priority order. Their associativity are left to right. Parenthesis can be used to change this order (or remove ambiguities).
 
 |without parenthesis|equivalent to|
 |-------------------|-------------|
 |`pred1 and pred2 or pred3 and pred4`|`(pred1 and pred2) or (pred3 and pred4)`|
 |`pred1 - pred2 - pred3`|`(pred1 - pred2) - pred3`|
 |`pred1 or pred2 - pred3 and pred4 or pred5`|`(pred1 or ((pred2 - pred3) and pred4)) or pred5`|
 
 Examples:
 * `/v1/coverage/id/lines?filter=physical_mode.id=physical_mode:Metro - stop_area.name=Nation - stop_area.name="Charles de Gaulle Etoile"` returns the metro lines that don't stop at Nation or Charles de Gaulle Etoile. Can also be written `/v1/coverage/id/lines?filter=physical_mode.id=physical_mode:Metro - (stop_area.name=Nation or stop_area.name="Charles de Gaulle Etoile")`
 * `/v1/coverage/id/lines?filter=stop_area.name=Nation and stop_area.name="Charles de Gaulle Etoile" - (stop_area.name=Bastille or stop_area.name=Corvisart)` returns the lines that stop at Nation and Charles de Gaulle Etoile but not at Bastille nor Corvisart.

## Sub request

## Some examples
