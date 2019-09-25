"""IFC data importer"""

import datetime as dt

from ifc_datareader import IfcDataReader

from .ifc_converter import IfcConverter, IfcConvertorError

from ...database import DBAccessor
from ...database.exceptions import ItemSaveError


class IfcImport():
    """IFC data import class"""

    def __init__(self, file_path, *, db_accessor=None):
        """
        :param str file_path: IFC file path to import.
        :param DBAccessor db_accessor: Database accessor to use to save data.
        """
        self._file_path = file_path

        self.report = []

        self._data_reader = IfcDataReader(self._file_path)
        self._log_to_report(
            'IfcDataReader', 'File {} loaded.'.format(self._file_path))

        self._db_accessor = db_accessor or DBAccessor()
        self._db_ids = {}

    def _log_to_report(self, head, message):
        self.report.append([head, dt.datetime.utcnow(), message])

    def _get_database_id(self, global_id):
        return self._db_ids.get(global_id, None)

    def _save_to_bd(self, ifc_item, model_item):
        db_item_id = self._db_accessor.create(model_item)
        self._db_ids[ifc_item.global_id] = db_item_id

    def _import_parent(self, item):
        parent_id = self._get_database_id(item.parent.global_id)
        if parent_id is None:
            self._log_to_report(
                'IfcImport', 'Item\'s parent not found.')
            raise TypeError
        return parent_id

    def _import(self, items, type_name, f_convert, get_parent=True):
        self._log_to_report(
            'IfcDataReader', 'Found {} {}(s)'.format(len(items), type_name))
        for cur_item in items:
            self._import_single(cur_item, type_name, f_convert, get_parent)
        self._log_to_report('IfcImport', 'All {}s done.'.format(type_name))

    def _import_single(self, item, type_name, f_convert, get_parent=True):
        try:
            model_item = f_convert(item, self._import_parent(item))\
                if get_parent else f_convert(item)
            self._save_to_bd(item, model_item)
            str_import_state = 'done'
        except (ItemSaveError, TypeError, IfcConvertorError):
            str_import_state = 'failed'
        self._log_to_report('IfcImport', 'Creating {} "{}"... {}'
                            .format(type_name, item.name, str_import_state))

    def execute(self):
        """Run the data importation."""

        #  Import sites
        self._log_to_report('IfcImport', 'Processing sites...')
        ifc_sites = self._data_reader.read_sites()
        self._import(ifc_sites, 'site', IfcConverter.to_site, False)

        # Import buildings
        self._log_to_report('IfcImport', 'Processing buildings...')
        ifc_buildings = self._data_reader.read_buildings()
        self._import(ifc_buildings, 'building', IfcConverter.to_building)

        #  import building storeys (floors)
        self._log_to_report(
            'IfcImport', 'Processing floors (building storeys)...')
        ifc_storeys = self._data_reader.read_building_storeys()
        self._log_to_report(
            'IfcDataReader', 'Found {} floor(s)'.format(len(ifc_storeys)))
        # first compute levels of building storeys
        sorted_ifc_storeys = sorted(
            ifc_storeys, key=lambda storey: storey.info.get('Elevation'))
        cur_level = min(
            0, -len([storey for storey in sorted_ifc_storeys
                     if storey.info.get('Elevation') < 0]))
        # Create building storeys
        for cur_ifc_storey in sorted_ifc_storeys:
            self._import_single(
                cur_ifc_storey, 'floor',
                lambda x, y: IfcConverter.to_floor(x, y, cur_level))
            cur_level += 1
        self._log_to_report('IfcImport', 'All floors done.')

        #  import spaces
        self._log_to_report('IfcImport', 'Processing spaces...')
        ifc_spaces = self._data_reader.read_spaces()
        self._import(ifc_spaces, 'space', IfcConverter.to_space)

        #  import zones
        self._log_to_report(
            'IfcImport', 'Processing zones...')
        ifc_zones = self._data_reader.read_zones()
        self._import(
            ifc_zones, 'zone',
            lambda x: IfcConverter.to_zone(
                x, lambda item: str(self._get_database_id(item.global_id))),
            get_parent=False)

        #  import walls
        self._log_to_report('IfcImport', 'Processing walls...')
        ifc_walls = self._data_reader.read_walls()
        self._import(
            ifc_walls, 'wall',
            lambda x: IfcConverter.to_facade(
                x, lambda item: str(self._get_database_id(item.global_id))),
            get_parent=False)

        #  import slabs
        self._log_to_report('IfcImport', 'Processing slabs...')
        ifc_slabs = self._data_reader.read_slabs()
        self._import(
            ifc_slabs, 'slab',
            lambda x: IfcConverter.to_slab(
                x, lambda item: str(self._get_database_id(item.global_id))),
            get_parent=False)

        #  import windows
        self._log_to_report('IfcImport', 'Processing windows...')
        ifc_windows = self._data_reader.read_windows()
        self._import(
            ifc_windows, 'window',
            lambda x: IfcConverter.to_window(
                x, lambda item: str(self._get_database_id(item.global_id)),
                self._data_reader),
            get_parent=False)
