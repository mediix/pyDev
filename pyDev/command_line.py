import argparse
import pprint as pp
from .DB_connect import set_connection

def main():
    # print "This is printing from command_line.py"
    '''Example of taking inputs for megazord bin'''
    parser = argparse.ArgumentParser(prog='pydev')
    parser.add_argument('-user', nargs='?', help='username')
    parser.add_argument('-passwd', nargs='?', help='password')
    parser.add_argument('-host', nargs='?', help='host')
    parser.add_argument('-port', nargs='?', help='port')
    parser.add_argument('-db', nargs='?', help='database')

    args = parser.parse_args()

    collected_inputs = {'user': args.user,
                        'pass': args.passwd,
                        'host': args.host,
                        'port': args.port,
                        'db':   args.db}
    print 'got input: ', pp.pprint(collected_inputs)

    try:
        engine = set_connection(args.user,
                                args.passwd,
                                args.host,
                                args.db,
                                args.port)
        connection = engine.connect()
    except Exception as err:
        raise ValueError(err)
    else:
        print "Connection successfully created."
    finally:
        connection.close()
        print "Connection successfully closed."

