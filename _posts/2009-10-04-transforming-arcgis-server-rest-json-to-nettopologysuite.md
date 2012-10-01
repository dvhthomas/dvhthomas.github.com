---
layout: post
title: "Transforming ArcGIS Server REST JSON to NetTopologySuite"
abstract: "I need to support a variety of geodata output formats like GML, KML, WKT. Using NetTopologySuite is a simple way to make it happen in an ArcGIS Server environment."
category: 
tags: [arcgis, geo]
---
Another quickie. I just wrote some code to get results from a Query against an ArcGIS Server REST server. I put a few classes together than represent fields, layers, and maps. Here the json output from a query is being passed to my helper function along with a list of fields that I’m interested in keeping, plus the geometry type (like esriPolygon). The wonderful part about this code is the way that [Json.NET](http://json.codeplex.com) assist me with it’s great LINQ implementation and fast forward-only `JsonTextReader`. In the method below I’m using the JsonTextReader: it takes a list of fields, and rips through the JSON result returned by the ESRI server. The returned value is a list of NetTopologySuite Features. This is the vanilla format that opens up doors to all sorts of interesting things.

{%highlight csharp%}
/// <summary>
/// Parses the results of a query operation against the layer
/// in to <see cref="Feature"/>s.
/// </summary>
/// <param name="dataSourceFields">List of valid fields</param>
/// <param name="geometryType"></param>
/// <param name="json"></param>
/// <returns></returns>
/// <remarks>Because the collection of fields can vary between each layer and even
/// between query results for each layer this actually has a two phased approach to loading
/// the data. First it loads the geometries using <see cref="Newtonsoft.Json.Linq"/> methods
/// ; this is possible because the structure of geometries is constant. Then it uses
/// a <see cref="JsonTextReader"/> to rip through the rest of the JSON content parsing
/// out the fields and their values. A bit awkward but really the only way to go given
/// the mutable list of fields, field names, and field values.</remarks>
private static IList<Feature> ReadLayerQueryResults(IEnumerable<Field> dataSourceFields, EsriGeometryType geometryType, string json)
{
    IList<Feature> features = null;
    if (string.IsNullOrEmpty(json)) return features;

    // First the geometries.
    IList<IGeometry> geometries = null;

    // TODO - I *think* this handles rasters and tables OK. but need to check again.
    if (geometryType != EsriGeometryType.NoGeometry)
    {
        geometries = RestClient.BuildGeometryFromJson(geometryType, json);
        if (geometries == null || geometries.Count == 0) return features;
    }

    var geometryIndex = 0;

    // Then the attributes
    JsonReader reader = new JsonTextReader(new StringReader(json));

    while (reader.Read())
    {
        while (Convert.ToString(reader.Value) != "features")
        {
            reader.Read();
        }

        // Found feature collections
        features = new List<Feature>();

        while (reader.Read())
        {
            var feature = new Feature();

            if (Convert.ToString(reader.Value) == "attributes")
            {
                // Found the attributes for a feature - this always comes
                // before the geometry if the geometry is even present
                IAttributesTable table = new AttributesTable();
                reader.Read();

                do
                {
                    // As long as we're still in the attribute list...
                    if (reader.TokenType == JsonToken.PropertyName)
                    {
                        var fieldName = Convert.ToString(reader.Value);
                        reader.Read();
                        Field field = dataSourceFields.SingleOrDefault(f => f.Name.ToUpperInvariant() == fieldName.ToUpperInvariant());
                        object value = reader.Value == null
                            ? null
                            : Convert.ChangeType(reader.Value, field.DataType);
                        if (!table.Exists(fieldName)) table.AddAttribute(fieldName, null);
                        table[fieldName] = value;
                    }

                    reader.Read();

                } while (reader.TokenType != JsonToken.EndObject
                         && Convert.ToString(reader.Value) != "attributes");

                feature.Attributes = table;

                if (geometries != null)
                {
                    feature.Geometry = geometries[geometryIndex];
                    geometryIndex++;
                }
            }

            // Was checking if feature null as well but a standalone table
            // in an MXD being served up does not have a spatial component
            // to turn in to geometries.
            if (feature.Attributes == null) continue;

            if (feature.Geometry != null & geometryType != EsriGeometryType.NoGeometry)
            {
                features.Add(feature);
            }
            else if (feature.Geometry == null & geometryType == EsriGeometryType.NoGeometry)
            {
                features.Add(feature);
            }
        }
    }

    return features;
}
{%endhighlight%}

In the next example I’m looping through the JSON result with a few lines of LINQ and getting fully built NetTopologySuite geometries that I can convert to GML, WKT, or another useful format. Or simply keep them as-is for analysis purposes.

{%highlight csharp%}
/// <summary>
/// Create valid <see cref="IGeometry"/> list from the incoming
/// JSON.
/// </summary>
/// <param name="geometryType">Only a single type of geometry is supported in each
/// query result, so the <paramref name="json"/> value is limited to one of the
/// <see cref="EsriGeometryType"/>s.</param>
/// <param name="json">JSON query result from <see cref="DownloadResource"/> which
/// is the raw JSON string.</param>
/// <returns>A list of point, polyline, polygon geometries in the same order
/// in which they are shown in the JSON input string.</returns>
public static IList<IGeometry> BuildGeometryFromJson(EsriGeometryType geometryType, string json)
{
    JObject jsonObject = JObject.Parse(json);
    IEnumerable<JToken> geometries = from g in jsonObject["features"].Children()
                     select g["geometry"];

    IList<IGeometry> list;
    switch (geometryType)
    {
        case EsriGeometryType.EsriGeometryPoint:
            IList<IGeometry> points = (from p in geometries
                          select new Point((double) p["x"], (double) p["y"], Double.NaN))
                .Cast<IGeometry>()
                .ToList();
            list = points;
            break;

        case EsriGeometryType.EsriGeometryPolygon:
            throw new NotImplementedException("Polygon deserialization from JSON has not been completed yet.");
            
        case EsriGeometryType.EsriGeometryPolyline:
            IList<IGeometry> lineStrings = new List<IGeometry>();

            IEnumerable<JEnumerable<JToken>> allPaths = from p in jsonObject["features"].Children()["geometry"]
                                    select p["paths"].Children();

            foreach (var eachPolylineInPath in allPaths)
            {
                ICoordinate[] linePoints = (from line in eachPolylineInPath.Children()
                               select new Coordinate((double) line[0], (double) line[1], double.NaN))
                    .Cast<ICoordinate>()
                    .ToArray();
                lineStrings.Add(new LineString(linePoints));
            }

            list = lineStrings;
            break;

        default:
            throw new ApplicationException(String.Format(Resources.UnsupportedGeometryType, geometryType));
    }

    return list;
}
{%endhighlight%}

Well, I haven't the polygon stuff yet (blush!) but you get the picture. Getting usable polylines from the JSON is literally two LINQ queries and one foreach . The simplicity is just a thing of beauty. Oh, and [props to this guy on StackOverflow](http://stackoverflow.com/questions/1423523/json-net-and-arrays-using-linq) for helping past a hurdle.
