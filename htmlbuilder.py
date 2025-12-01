from bs4 import BeautifulSoup, Tag
from enum import Enum

class Header(Enum):
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6

class CellType(Enum):
    TD = 1
    TH = 2

class HtmlBuilder:
    def __init__(self):
        self.__soup = BeautifulSoup('<html><body/></html>','html.parser')
        self.__body = self.__soup.body

    def Save(self, htmlFileName : str):
        with open(htmlFileName, 'w') as f:
            f.write(self.__soup.prettify())

    def NewTable(self, attrs) -> Tag:
        table : Tag = self.__soup.new_tag('table')
        for attr_name, attr_value in attrs.items():
            table[attr_name] = attr_value
        self.__body.append(table)
        return table

    def InsertNewHeader(self, h_type : Header, h_str : str):
        h_tag : Tag = self.__soup.new_tag(h_type.name)
        h_tag.string = h_str
        self.__body.append(h_tag)
    
    def NewTableRow(self,tableToAppendTo : Tag) -> Tag:
        tr : Tag = self.__soup.new_tag('tr')
        tableToAppendTo.append(tr)
        return tr

    def NewTableCell(self, c_type : CellType, tableRowToAppendTo : Tag, c_str : str = None, c_span : int = 1) -> Tag:
        cell : Tag = self.__soup.new_tag(c_type.name)
        cell.string = str(c_str)
        cell.attrs['colspan'] = c_span
        tableRowToAppendTo.append(cell)
        return cell
        
