from flask import Flask, jsonify, request
import sqlite3


app = Flask('My App')
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


def convert_ipv4(ip):
    try:
        return tuple(int(n) for n in ip.split('.'))
    except ValueError:
        pass


def check_ipv4_in(addr, start, end):
    a = convert_ipv4(start)
    b = convert_ipv4(addr)
    c = convert_ipv4(end)

    if all(v is not None for v in [a, b, c]):
        return a < b < c
    else:
        return False


@app.route('/ASN_api/getasn', methods=['GET'])
def get_asn():
    """
    http://127.0.0.1:5000/ASN_api/getasn?asn_num=13335

    """

    con = sqlite3.connect("ip2asn-combined.sqlite")
    cur = con.cursor()
    asn_num = request.args.get('asn_num', type=int)

    if type(asn_num) is not int:
        return 'Input not valid!', 400

    sql_exec = cur.execute('SELECT * FROM ip2asn WHERE AS_number='+str(asn_num)+';')
    json_dump = sql_exec.fetchall()

    con.close()

    return jsonify({'columns': [x[0] for x in sql_exec.description], 'data': json_dump}), 200


@app.route('/ASN_api/getip', methods=['GET'])
def get_ip():
    """
    http://127.0.0.1:5000/ASN_api/getip?ip=1.0.5.0

    """

    con = sqlite3.connect("ip2asn-combined.sqlite")
    cur = con.cursor()
    ip = request.args.get('ip')
    res_lst = []

    for row in cur.execute('SELECT * FROM ip2asn;'):
        if check_ipv4_in(ip, *(row[0], row[1])):
            res_lst.append(row)

    con.close()

    if len(res_lst) == 0:
        return 'Input not valid!', 400

    return jsonify(range_start=res_lst[0][0], range_end=res_lst[0][1],
                   AS_number=res_lst[0][2], country_code=res_lst[0][3],
                   AS_description=res_lst[0][4], input_ip=ip), 200


if __name__ == '__main__':
    app.run()
