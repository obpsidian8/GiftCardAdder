import requests
import json


class ProcessGiftCards():
    def __init__(self, user_email, promo_name, gc_limit):
        self.user_email = user_email
        self.promo_name = promo_name
        self.gc_limit = gc_limit

    def get_url_endpoint(self):
        self.url_endpoint = f"http://192.168.1.8/pytestapi/odata/GiftCardRecords?$expand=GiftCardItems&$orderby=CreatedOn desc&$filter=ReceivedEmailAddress eq '{self.user_email}' and PromotionName eq '{self.promo_name}' and PromotionText ne '$0.00' and PromotionText ne 'er000' "

        return self.url_endpoint

    def get_gift_card(self):
        print(f"\nGetting giftcard for {self.user_email}")
        promo_code_site_response = requests.get(self.get_url_endpoint())
        data = promo_code_site_response.json()
        all_codes = data['value']

        if len(all_codes) == 0 or all_codes is None:
            url_end_point_2 = f"http://192.168.1.8/pytestapi/odata/GiftCardRecords?$expand=GiftCardItems&$orderby=CreatedOn desc&$filter=PromotionName  eq '{self.promo_name}' and PromotionText ne '$0.00' and PromotionText ne 'er000' "

            print(f"\nGetting giftcard for {self.user_email}")
            promo_code_site_response = requests.get(url_end_point_2)
            data = promo_code_site_response.json()
            all_codes = data['value']

        print("\nChecking for un-used codes")

        self.giftcards_to_use = []
        code_found = False
        print("Going to check with email and code status")

        for entry in all_codes:
            if (entry['ReceivedEmailAddress']) is not None:
                email = str(entry['ReceivedEmailAddress']).lower()

                if str(entry['Status']) not in ('used', 'Used', 'expired', 'Expired') and email == self.user_email and str(
                        entry['PromotionName']) == self.promo_name and str(entry['PromotionText']) != "$0.00" and str(entry['PromotionText']) != "er000" and (entry['Notes']) is None:

                    promo_code = entry['PromotionCode']
                    promo_pin = entry['PromotionPin']
                    amount = entry['PromotionText']
                    code_found = True

                    current_order_record = {'GCCODE': promo_code,
                                            'PIN': promo_pin,
                                            'AMOUNT':amount
                                            }

                    self.giftcards_to_use.append(current_order_record)

                    if len(self.giftcards_to_use) >= self.gc_limit:
                        break

        if len(self.giftcards_to_use) < self.gc_limit:
            student_deal_url_end_point = f"http://192.168.1.8/pytestapi/odata/GiftCardRecords?$expand=GiftCardItems&$orderby=CreatedOn desc&$filter=PromotionName eq '{self.promo_name}' and PromotionText ne '$0.00' and PromotionText ne 'er000'  and Notes eq null"

            print(f"\nGetting giftcard for {self.user_email}")
            promo_code_site_response = requests.get(student_deal_url_end_point)
            data = promo_code_site_response.json()
            all_codes = data['value']

            print("Could not match email address of current user to email address on codes. Going to search just based on code status.")
            for entry in all_codes:
                if str(entry['Status']) not in ('used', 'Used', 'expired', 'Expired') and str(entry['PromotionName']) == self.promo_name and str(
                        entry['PromotionText']) != "$0.00" and str(entry['PromotionText']) != "er000" and (entry['Notes']) is None:
                    promo_code = entry['PromotionCode']
                    promo_pin = entry['PromotionPin']
                    amount = entry['PromotionText']

                    current_order_record = {'GCCODE': promo_code,
                                            'PIN': promo_pin,
                                            'AMOUNT': amount
                                            }

                    self.giftcards_to_use.append(current_order_record)

                    if len(self.giftcards_to_use) >= self.gc_limit:
                        break

        return self.giftcards_to_use

    def update_promo_code_status(self, status, order_number):

        for gift_card in self.giftcards_to_use:
            promo_code = gift_card['GCCODE']
            notes = f"Used on Order {order_number}"
            status = status

            get_code_url = f"http://192.168.1.71/pytestapi/odata/GiftCardRecords?$expand=GiftCardItems&$orderby=CreatedOn desc&$filter=PromotionCode eq '{promo_code}'"

            print(f"Getting code details for  for {promo_code}")
            promo_code_site_response = requests.get(get_code_url)
            data = promo_code_site_response.json()
            codes_detail = data['value'][0]

            update_info = {
                "Id": codes_detail['Id'],
                "SellerId": None,
                "SiteName": codes_detail['SiteName'],
                "Status": status,
                "EmailMessageId": codes_detail['EmailMessageId'],
                "EmailSubject": codes_detail['EmailSubject'],
                "FromEmailAddress": codes_detail['FromEmailAddress'],
                "ReceivedEmailAddress": codes_detail['ReceivedEmailAddress'],
                "PromotionName": codes_detail['PromotionName'],
                "PromotionCode": promo_code,
                "PromotionPin": codes_detail['PromotionPin'],
                "PromotionText": codes_detail['PromotionText'],
                "PromotionSkus": codes_detail['PromotionSkus'],
                "PromotionUrl": codes_detail['PromotionUrl'],
                "PromotionPictureUrl": codes_detail['PromotionPictureUrl'],
                "Notes": notes,
                "OrderId": None,
                "DiscountAmount": None,
                "QuantityRequired": None,
                "QuantityLimit": None,
                "IsMultipleSkus": None,
                "IsPercentOff": None,
                "IsOneTimeUse": None,
                "IsPrivate": None,
                "IsExpired": None,
                "StartOn": None,
                "ExpireOn": None,
                "CreatedOn": codes_detail['CreatedOn'],
                "UsedOn": None
            }

            post_info_url = f"http://192.168.1.8/pytestapi/odata/GiftCardRecords({codes_detail['Id']})"

            try:
                print(update_info)
                jsonstr = json.dumps(update_info)
                print(jsonstr)

                headers = {'Content-type': 'application/json'}
                response = requests.put(post_info_url, data=jsonstr, headers=headers)

                response.raise_for_status()

                data = response.json()
                print("update posted.")
            except Exception as e:
                print(f"SellerPromotion {e}")


def test_class():
    new_newegg_gift_card = ProcessGiftCards("pytest@pytest.com", "test_run_4", 1)

    print(f"{new_newegg_gift_card.user_email}")
    print(f"{new_newegg_gift_card.promo_name}")
    print(f"{new_newegg_gift_card.get_url_endpoint()}")
    print(f"{new_newegg_gift_card.get_gift_card()}")

    status = "Used"
    order_number = "PY12312018"

    new_newegg_gift_card.update_promo_code_status(status, order_number)


if __name__ == '__main__':
    test_class()
