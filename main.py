# main.py
import attUtils

def main():
    print("===============================bulkOrders_GLS")
    attUtils.prepare_bulkOrders_GLS()
    print("===============================bulkOrders_FR")
    attUtils.prepare_bulkOrders_FR()
    print("===============================Sucess")

if __name__ == "__main__":
    main()