from emerge import fs

customer = fs.getobject("/customers/Customer-0", False)

print(customer.farms[0])
