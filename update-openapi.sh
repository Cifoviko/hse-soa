#!/bin/bash

pairs=(
    "service-users http://127.0.0.1:8000/apispec_1.json"
)

for pair in "${pairs[@]}"; do
    # Разбиваем пару на переменные first и second
    service=$(echo $pair | cut -d' ' -f1)
    url=$(echo $pair | cut -d' ' -f2)

    curl -o apispec_1.json "$url"

    python3 -c 'import yaml, sys; print(yaml.dump(yaml.load(open(sys.argv[1])), default_flow_style=False))' apispec_1.json > ./$service/api-spec.yaml

    rm apispec_1.json
done
