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
