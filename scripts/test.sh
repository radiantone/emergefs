python emerge/example/widgets.py 
python emerge/example/query.py 
emerge methods /inventory/widget7
emerge cat /inventory/widget1
emerge help  /inventory/widget1
emerge ls
emerge ls -l
emerge ls /inventory
emerge ls -l /inventory
emerge query /queries/query1
emerge call -l /inventory/widget5 total_cost
emerge call /inventory/widget5 total_cost
emerge --debug call -l /inventory/widget5 total_cost
emerge --debug call /inventory/widget3 total_cost
emerge rm /inventory
emerge call /inventory total_cost
emerge code /inventory/widget1
emerge search data data
python emerge/example/proxy.py
emerge graphql "$(cat query3.json)"

python emerge/example/widget2a.py
emerge -h localhost:5559 ls -l
emerge -h localhost:5559 ls -l /inventory
emerge -h localhost:5559 cat /inventory/widget2a


emerge rm /inventory/widget1
emerge rm /inventory/widget2
emerge rm /inventory/widget3
emerge rm /inventory/widget4
emerge rm /inventory/widget5
emerge rm /inventory/widget6
emerge rm /inventory/widget7
emerge rm /inventory/widget8
emerge rm /inventory/widget9
emerge rm /inventory
emerge ls -l
