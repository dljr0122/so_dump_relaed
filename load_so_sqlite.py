import sqlite3
import os
import xml.etree.cElementTree as etree
import logging
import sys

ANATHOMY = {
    'Badges': {
        'Id': 'INTEGER',
        'UserId': 'INTEGER',
        'Class': 'INTEGER',
        'Name': 'TEXT',
        'Date': 'DATETIME',
        'TagBased': 'BOOLEAN',
        },
    'Comments': {
        'Id': 'INTEGER',
        'PostId': 'INTEGER',
        'Score': 'INTEGER',
        'Text': 'TEXT',
        'CreationDate': 'DATETIME',
        'UserId': 'INTEGER',
        'UserDisplayName': 'TEXT',
        },
    'Posts': {
        'Id': 'INTEGER',
        'PostTypeId': 'INTEGER', 
        'ParentId': 'INTEGER',
        'AcceptedAnswerId': 'INTEGER',
        'CreationDate': 'DATETIME',
        'Score': 'INTEGER',
        'ViewCount': 'INTEGER',
        'Body': 'TEXT',
        'OwnerUserId': 'INTEGER',
        'OwnerDisplayName': 'TEXT',
        'LastEditorUserId': 'INTEGER',
        'LastEditorDisplayName': 'TEXT',
        'LastEditDate': 'DATETIME',
        'LastActivityDate': 'DATETIME',
        'CommunityOwnedDate': 'DATETIME',
        'Title': 'TEXT',
        'Tags': 'TEXT',
        'AnswerCount': 'INTEGER',
        'CommentCount': 'INTEGER',
        'FavoriteCount': 'INTEGER',
        'ClosedDate': 'DATETIME'
        },
    'Votes': {
        'Id': 'INTEGER',
        'PostId': 'INTEGER',
        'UserId': 'INTEGER',
        'VoteTypeId': 'INTEGER',
        'CreationDate': 'DATETIME',
        'BountyAmount': 'INTEGER'
        },
    'PostHistory': {
        'Id': 'INTEGER',
        'PostHistoryTypeId': 'INTEGER',
        'PostId': 'INTEGER',
        'RevisionGUID': 'TEXT',
        'CreationDate': 'DATETIME',
        'UserId': 'INTEGER',
        'UserDisplayName': 'TEXT',
        'Comment': 'TEXT',
        'Text': 'TEXT'
        },
    'PostLinks': {
            'Id': 'INTEGER',
            'CreationDate': 'DATETIME',
            'PostId': 'INTEGER',
            'RelatedPostId': 'INTEGER',
            'PostLinkTypeId': 'INTEGER',
            'LinkTypeId': 'INTEGER',
        },
    'Users': {
            'Id': 'INTEGER',
            'Reputation': 'INTEGER',
            'CreationDate': 'DATETIME',
            'DisplayName': 'TEXT',
            'LastAccessDate': 'DATETIME',
            'WebsiteUrl': 'TEXT',
            'Location': 'TEXT',
            'Age': 'INTEGER',
            'AboutMe': 'TEXT',
            'Views': 'INTEGER',
            'UpVotes': 'INTEGER',
            'DownVotes': 'INTEGER',
            'AccountId': 'INTEGER',
            'ProfileImageUrl': 'TEXT'
       },
    'Tags': {
            'Id': 'INTEGER',
            'TagName': 'TEXT',
            'Count': 'INTEGER',
            'ExcerptPostId': 'INTEGER',
            'WikiPostId': 'INTEGER'
        }
}

def dump_files(file_names, anathomy,
        so_xml_path='/media/sf_vb-shared/so_dump',
        dump_path='.',
        dump_database_name='so-dump.db',
        create_query='CREATE TABLE IF NOT EXISTS {table} ({fields})',
        insert_query='INSERT INTO {table} ({columns}) VALUES ({values})',
        log_filename='so-parser.log'):
    logging.basicConfig(filename=os.path.join(dump_path, log_filename), level=logging.INFO)
    db = sqlite3.connect(os.path.join(dump_path, dump_database_name))
    for file in file_names:
        print("Opening {0}.xml".format(file))
        with open(os.path.join(so_xml_path, file + '.xml')) as xml_file:
            tree = etree.iterparse(xml_file)
            table_name = file

            sql_create = create_query.format(
                    table=table_name,
                    fields=", ".join(['{0} {1}'.format(name, type) for name, type in anathomy[table_name].items()]))
            print('Creating table {0}'.format(table_name))

            try:
                logging.info(sql_create)
                db.execute(sql_create)
            except Exception as e:
                logging.warning(e)

            count = 0
            for events, row in tree:
                try:
                    if row.attrib.values():
                        logging.debug(row.attrib.keys())
                        query = insert_query.format(
                                table=table_name,
                                columns=', '.join(row.attrib.keys()),
                                values=('?, ' * len(row.attrib.keys()))[:-2])
                        vals = []
                        for key, val in row.attrib.items():
                            if anathomy[table_name][key] == 'INTEGER':
                                vals.append(int(val))
                            elif anathomy[table_name][key] == 'BOOLEAN':
                                vals.append(1 if val=="TRUE" else 0)
                            else:
                                vals.append(val)
                        db.execute(query, vals)

                        count += 1
                        if (count % 1000 == 0):
                            print("{}: {}".format(file, count))

                except Exception as e:
                    logging.warning(e)
                    print("x", end="")
                finally:
                    row.clear()
            print("\n")
            db.commit()
            del (tree)


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 2:
        so_xml_path = sys.argv[1]
    else:
        so_xml_path = '/media/sf_vb-shared/so_dump'

    dump_files(ANATHOMY.keys(), ANATHOMY, so_xml_path=so_xml_path)

