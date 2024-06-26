# cjseqview

A small python program to visualise [CityJSONSeq](https://cityjson.org/cityjsonseq) datasets.

![](demo.png)

## Dependencies

```bash
pip install mapbox_earcut
pip install polyscope
pip install numpy
pip install click
```

## Using cjseqview

It reads a [CityJSONSeq](https://cityjson.org/cityjsonseq) from stdin.

```bash
cat ./data/b2.city.jsonl | python ./src/cjseqview.py
```

```bash
cjio --suppress_msg Vienna_102081.city.json subset --random 5 export jsonl stdout | python ./src/cfseqview.py --lod_filter 2
```


