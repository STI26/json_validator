from functools import reduce
from typing import Union, List, Tuple


def json_type_to_python_type(
        json_type: Union[str, List[str]]) -> Union[type, Tuple[type]]:
    """
    Convert json type to python type.
    """

    json_types = {
        'string': (str,),
        'number': (int, float,),
        'integer': (int,),
        'object': (dict,),
        'array': (list, tuple,),
        'boolean': (bool,),
        'null': (type(None),)
    }

    if isinstance(json_type, list):
        # if more than one type is allowed
        return reduce(lambda a, b: a+b, [json_types[i] for i in json_type])
    else:
        return json_types[json_type]


def export_to_html(array: list):
    html_head = '''
    <head>
        <style>
            table {
                width: 100%;
            }
            table, th, td {
                border: 1px solid #ccc;
                margin: 0 auto;
                border-spacing: 0;
            }
            th, td {
                padding: 5px;
            }
            tr.invalid {
                background-color: #ffe1e1;
            }
            tr.valid {
                background-color: #e1e1ff;
            }
            h3 {
                text-align: center;
            }
        </style>
    </head>
    '''

    html_table_head = '''
    <tr>
        <th>#</th>
        <th>file name</th>
        <th>schema</th>
        <th>status</th>
        <th>errors</th>
    </tr>
    '''

    html_table_body = ''
    for idx, r in enumerate(array):
        html_table_body_row = '''
        <tr class="{cls}">
            <td>{index}</td>
            <td>{file}</td>
            <td>{schema}</td>
            <td>{status}</td>
            <td>{errors}</td>
        </tr>
        '''

        html_list_errors = '<ul><li>{}</li></ul>'.format(
            '</li><li>'.join(r.errors)
        )

        html_table_body += html_table_body_row.format(
            cls=r.status.lower(),
            index=idx + 1,
            file=r.file_name,
            schema=r.schema_name,
            status=r.status,
            errors=html_list_errors if r.errors else ''
        )

    html_body_title = '<h3>Total files: {}; Invalid files: {}</h3>'.format(
        len(array), sum(1 for item in array if item.status == 'Invalid')
    )
    checkbox = '''
    <label>Valid:<input type="checkbox" id="valid" checked /></label>
    <label>Invalid:<input type="checkbox" id="invalid" checked /></label>
    '''

    js_block = '''
    <script>
        const valids = document.querySelectorAll('tr.valid');
        const invalids = document.querySelectorAll('tr.invalid');
        function showRows(nodes, flag) {
            if (flag === true) {
                nodes.forEach((el) => {
                    el.style.display = "table-row";
                });
            } else {
                nodes.forEach((el) => {
                    el.style.display = "none";
                });
            }
        }
        document.querySelector('#valid').addEventListener('change', (el) => {
            showRows(valids, el.target.checked);
        });
        document.querySelector('#invalid').addEventListener('change', (el) => {
            showRows(invalids, el.target.checked);
        });
    </script>
    '''

    with open('report.html', 'w') as f:
        f.write(html_head)
        f.write('<body><table>')
        f.write(html_body_title)
        f.write(checkbox)
        f.write(html_table_head)
        f.write(html_table_body)
        f.write('</table>')
        f.write(js_block)
        f.write('</body>')
