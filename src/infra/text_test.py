# Created by Patrick Kao
from twilio.rest import Client

client = Client("AC46e4ac967021aac04155bc42bbd2cb8a", "876df1548202229c46da2032a0a8bee1")


client.messages.create(to="+16508344535",
                       from_="+14153199415",
                       body="Hello from Python!")