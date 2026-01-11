```bash
poetry run python src/silvervector/examples/init_ecommerce.py
```


```bash
cd src/silvervector/

docker run -d -p 3000:3000 \
  -v "$(pwd)/examples:/var/lib/grafana/silvervector_data" \
  -e "GF_INSTALL_PLUGINS=frser-sqlite-datasource" \
  --name=silvervector-grafana grafana/grafana-oss
```

Once Grafana is running at http://localhost:3000:

1. Navigate to Connections > Data Sources;
2. Search for SQLite;
3. In the Path field, enter the container path: /var/lib/grafana/silvervector_data/silvervector_demo.db.