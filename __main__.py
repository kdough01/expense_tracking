from receipt import get_receipt_text, get_total, get_items

# Example receipt
store_string = """OTARGET

GreenWood City - 888 -888-8888
GreenWood City, CA, 34343-343343
08/19/2021 17:32:29 EXPIRES 11/17/2021

ELECTRONICS

7053275 BIG 42 Inch LED TVN 533.89
DISCOUNT COUPON N -50.00
5599903 Bluetooth F 29.99

HEALTH AND BEAUTY
1542666 Dave Shanpoo N 12.98
5044148 Dave Conditioner N 8.99
SUBTOTAL 535.85
T = CA TAX 9.7500% on 535.85 49.89
TOTAL 585.74
*9999 VISA CHARGE 585.74

REC#2-6965-3530-9288-3901-2 VCD#352-663-321

Thank You
Please Come Again"""

# print(get_receipt_text(receipt_img = "test.png"))
print(get_items(text = store_string))