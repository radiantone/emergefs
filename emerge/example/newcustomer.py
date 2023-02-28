from emerge.example.customers import datetime, field, uuid4, emerge, dataclass, Customer

@dataclass
class RegionCustomer(Customer):
    latlng: list = field(default_factory=list)

    def region(self):
        return 'east' if self.latlng[0] > 4 else 'west'
    
    def hello(self):
        return "Hello there!"
    
    def error(self):
        return self.latlng

now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

customer = RegionCustomer(
    id="RegionCustomerA",
    name="RegionCustomerA",
    perms="rwxrwxrwx",
    path="/customers",
    data="A region customer data",
    customerId = str(uuid4()),
    createdOn=now,
    createTimeStamp=now,
    latlng=[5,-20],
    version=0)

customer = RegionCustomer(
    id="RegionCustomerA",
    name="RegionCustomerA",
    perms="rwxrwxrwx",
    path="/customers",
    data="A region customer data",
    customerId = str(uuid4()),
    createdOn=now,
    createTimeStamp=now,
    latlng=[5,-20],
    version=1)

print(customer)
emerge.store(customer)