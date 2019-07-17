from lib.types.function import Function


class ModuleInfo:

    def __init__(self, module_base_info):
        self._updated_details = False

        self.name = module_base_info['name']
        self.base = int(module_base_info['base'], 16)
        self.size = module_base_info['size']
        self.path = module_base_info['path']

        self.sections = {}

        self.functions = []
        self.functions_map = {}

        # frida objects
        self.exports = []
        self.imports = []
        self.symbols = []

    @property
    def have_details(self):
        return self._updated_details

    @staticmethod
    def build_module_info(dwarf, name_or_address, fill_ied=False):
        module_base_info = dwarf.dwarf_api('findModule', name_or_address)
        if module_base_info is not None:
            module_info = ModuleInfo(module_base_info)

            if fill_ied:
                module_info.update_details(dwarf)

            return module_info
        return None

    def apply_symbols(self, module_symbols):
        self.symbols = module_symbols
        for symbol in module_symbols:
            if 'section' in symbol:
                section = symbol['section']
                section_id = section['id']

                if section_id not in self.sections:
                    self.sections[section_id] = section

            self.parse_symbol(symbol)

    def apply_imports(self, imports):
        self.imports = imports
        for import_ in imports:
            self.parse_symbol(import_)

    def apply_exports(self, exports):
        self.exports = exports
        for export in exports:
            self.parse_symbol(export)

    def parse_symbol(self, symbol):
        type_ = symbol['type']
        if type_ == 'function':
            if symbol['address'] not in self.functions_map:
                f = Function(symbol)
                self.functions.append(f)
                self.functions_map[symbol['address']] = f

    def update_details(self, dwarf):
        self._updated_details = True

        symbols = dwarf.dwarf_api('enumerateSymbols', self.base)
        self.apply_symbols(symbols)
        imports = dwarf.dwarf_api('enumerateImports', self.base)
        self.apply_imports(imports)
        exports = dwarf.dwarf_api('enumerateExports', self.base)
        self.apply_exports(exports)
