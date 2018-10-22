# coding: utf-8

from bs4 import BeautifulSoup
import unicodedata


class TableParser:

    def __init__(self):
        self.hello = "HTML Table Parser!"

    def parse_header(self, all_text):

        try:

            soup = BeautifulSoup(all_text, 'html.parser')
            info = soup.find_all('sec-header')
            all_list = []

            for item in info:
                all_list.append(item.get_text())

            header_str = ''.join(all_list)

            for line in header_str.splitlines():

                if not line:
                    continue

                elif 'CONFORMED PERIOD OF REPORT' in line:
                    key_value = line.split(':')
                    value = key_value[1].strip()
                    return self.get_quarter(value), self.get_year(value)

        except Exception as e:
            print 'Exception in parse_header!'
            print e
            return 'NA', 'NA'

    def get_quarter(self, date_str):

        month = date_str[4:6]
        month_int = int(month)

        for months, quarter in [
            ([1, 2, 3], 1),
            ([4, 5, 6], 2),
            ([7, 8, 9], 3),
            ([10, 11, 12], 4)
        ]:
            if month_int in months:
                return quarter

    def get_year(self, date_str):

        year = date_str[0:4]
        return int(year)

    # def get_num_var_exceptions(self, sub_text):

    def parse_html_table(self, table):
        table_str = ''
        rows = table.find_all('tr')
        for row in rows:
            td_tags = row.find_all('td')
            for ele in td_tags:
                entry = ele.get_text()
                table_str = table_str + ' col ' + entry
            table_str = table_str + ' row '

        table_str = unicodedata.normalize('NFKD', table_str).encode('ascii', 'ignore')
        table_str_rows = table_str.split(' row ')
        rc = [row.split(' col ') for row in table_str_rows]

        for idx_row in range(len(rc)):
            row = rc[idx_row]
            for col_idx in range(len(row)):
                item = row[col_idx]
                item = item.replace('\n', '').replace('\t', '').replace('\r', '')
                rc[idx_row][col_idx] = self.clean_cell_value(item)
        rc_cleaned = [filter(None, row) for row in rc]
        return rc_cleaned

    def clean_cell_value(self, cell_value):

        cell_value = " ".join(cell_value.split())

        all_char_replace = [')', '$', '%']

        for char in all_char_replace:
            if char in cell_value:
                cell_value = cell_value.replace(char, '')

        if '(' in cell_value and len(cell_value) <= 5:
            cell_value = cell_value.replace('(', '')

            flag = False
            replace_char = ['a', 'b', 'c', 'd']
            for char_sub in replace_char:
                if char_sub in cell_value:
                    flag = True
                    cell_value = cell_value.replace(char_sub, '')

            if not flag:
                cell_value = '-' + cell_value

        return cell_value.strip()