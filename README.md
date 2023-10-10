# viewcjl

A small python program to visualise CityJSONL datasets.

![](demo.png)

## dependencies

```bash
pip install mapbox_earcut
pip install polyscope
pip install numpy
```

## Using viewcjl

It reads from stdin a [CityJSONL file](https://cityjson.org/cityjsonl)

```bash
bat ./data/b2.city.jsonl | python ./src/viewcjl.py
```

```bash
cjio --suppress_msg Vienna_102081.city.json subset --random 5 export jsonl stdout | python ./src/viewcjl.py
