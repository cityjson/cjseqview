# viewcjl

A small python program to visualise CityJSONL datasets.

![](demo.png)

## Dependencies

```bash
pip install mapbox_earcut
pip install polyscope
pip install numpy
```

## Using viewcjl

It reads a [CityJSONL file](https://cityjson.org/cityjsonl) from stdin.

```bash
cat ./data/b2.city.jsonl | python ./src/viewcjl.py
```

```bash
cjio --suppress_msg Vienna_102081.city.json subset --random 5 export jsonl stdout | python ./src/viewcjl.py
```


