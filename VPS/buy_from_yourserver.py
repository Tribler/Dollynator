from YourserverBuyer import YourserverBuyer

buyer = YourserverBuyer()
result = buyer.place_order()

if result == True:
    print("VPS BOUGHT! Details:")
    print("Yourserver email: " + buyer.get_email())
    print("Yourserver password: " + buyer.get_password())
    print("SSH IP: " + buyer.get_ip())
    print("SSH Username: " + buyer.get_ssh_username())
    print("SSH Password: " + buyer.get_ssh_password())
else:
    print("Failed to buy VPS from Yourserver...")
