"""
Processador de arquivos IFC para extração de metadados e geometrias.
Utiliza IfcOpenShell para leitura e interpretação de arquivos IFC.
"""

import ifcopenshell
import ifcopenshell.geom
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class IFCProcessor:
    """
    Processa arquivos IFC e extrai metadados estruturados.
    """
    
    def __init__(self, ifc_file_path: str):
        """
        Inicializa o processador com caminho do arquivo IFC.
        
        Args:
            ifc_file_path: Caminho completo para o arquivo IFC
        """
        self.file_path = ifc_file_path
        self.model = None
        
    def open(self) -> bool:
        """
        Abre o arquivo IFC.
        
        Returns:
            bool: True se o arquivo foi aberto com sucesso, False caso contrário
        """
        try:
            self.model = ifcopenshell.open(self.file_path)
            logger.info(f"Arquivo IFC aberto com sucesso: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao abrir arquivo IFC: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Extrai informações gerais do projeto IFC.
        
        Returns:
            dict: Informações do projeto (nome, descrição, schema, etc.)
        """
        if not self.model:
            return {}
        
        try:
            project = self.model.by_type("IfcProject")[0]
            
            return {
                'name': project.Name or 'Sem nome',
                'description': project.Description or '',
                'schema': self.model.schema,
                'total_elements': len(self.model.by_type("IfcProduct")),
            }
        except Exception as e:
            logger.error(f"Erro ao extrair informações do projeto: {e}")
            return {}
    
    def get_building_elements(self) -> Dict[str, List[Dict]]:
        """
        Extrai elementos do edifício organizados por tipo.
        
        Returns:
            dict: Elementos organizados por tipo (paredes, lajes, colunas, etc.)
        """
        if not self.model:
            return {}
        
        element_types = [
            "IfcWall", "IfcSlab", "IfcColumn", "IfcBeam", 
            "IfcDoor", "IfcWindow", "IfcSpace", "IfcStair",
            "IfcRoof", "IfcRailing", "IfcPlate", "IfcMember",
            "IfcCovering", "IfcCurtainWall", "IfcBuildingElementProxy"
        ]
        
        elements_by_type = {}
        
        for element_type in element_types:
            try:
                elements = self.model.by_type(element_type)
                if not elements:
                    continue
                    
                elements_by_type[element_type] = []
                
                for element in elements:
                    elements_by_type[element_type].append({
                        'id': element.id(),
                        'global_id': element.GlobalId,
                        'name': element.Name or f'{element_type}_{element.id()}',
                        'description': element.Description or '',
                        'type': element_type
                    })
            except Exception as e:
                logger.warning(f"Erro ao processar tipo {element_type}: {e}")
                continue
        
        return elements_by_type
    
    def get_element_properties(self, element_id: int) -> Dict[str, Any]:
        """
        Extrai propriedades de um elemento específico.
        
        Args:
            element_id: ID do elemento IFC
            
        Returns:
            dict: Propriedades do elemento
        """
        if not self.model:
            return {}
        
        try:
            element = self.model.by_id(element_id)
            
            properties = {
                'id': element.id(),
                'global_id': element.GlobalId,
                'name': element.Name or '',
                'type': element.is_a(),
                'description': element.Description or '',
                'properties': {}
            }
            
            # Extrair property sets
            if hasattr(element, 'IsDefinedBy'):
                for definition in element.IsDefinedBy:
                    if definition.is_a('IfcRelDefinesByProperties'):
                        property_set = definition.RelatingPropertyDefinition
                        if property_set.is_a('IfcPropertySet'):
                            properties['properties'][property_set.Name] = {}
                            for prop in property_set.HasProperties:
                                if prop.is_a('IfcPropertySingleValue'):
                                    try:
                                        value = str(prop.NominalValue.wrappedValue) if prop.NominalValue else 'N/A'
                                        properties['properties'][property_set.Name][prop.Name] = value
                                    except:
                                        properties['properties'][property_set.Name][prop.Name] = 'N/A'
            
            # Extrair material
            if hasattr(element, 'HasAssociations'):
                for association in element.HasAssociations:
                    if association.is_a('IfcRelAssociatesMaterial'):
                        material = association.RelatingMaterial
                        if material.is_a('IfcMaterial'):
                            properties['material'] = material.Name
                        elif material.is_a('IfcMaterialLayerSetUsage'):
                            properties['material'] = material.ForLayerSet.MaterialLayers[0].Material.Name
            
            return properties
        except Exception as e:
            logger.error(f"Erro ao extrair propriedades do elemento {element_id}: {e}")
            return {'error': str(e)}
    
    def get_spatial_structure(self) -> List[Dict]:
        """
        Extrai estrutura espacial hierárquica do IFC.
        
        Returns:
            list: Estrutura hierárquica (projeto -> site -> edifício -> andar -> espaços)
        """
        if not self.model:
            return []
        
        try:
            project = self.model.by_type("IfcProject")[0]
            structure = []
            
            if hasattr(project, 'IsDecomposedBy'):
                for rel in project.IsDecomposedBy:
                    for site in rel.RelatedObjects:
                        site_data = self._get_spatial_node(site)
                        structure.append(site_data)
            
            return structure
        except Exception as e:
            logger.error(f"Erro ao extrair estrutura espacial: {e}")
            return []
    
    def _get_spatial_node(self, element) -> Dict:
        """
        Helper recursivo para construir estrutura espacial.
        
        Args:
            element: Elemento IFC espacial
            
        Returns:
            dict: Nó da estrutura com filhos
        """
        node = {
            'id': element.id(),
            'global_id': element.GlobalId,
            'name': element.Name or f'{element.is_a()}_{element.id()}',
            'type': element.is_a(),
            'description': element.Description or '',
            'children': []
        }
        
        # Processar elementos contidos
        if hasattr(element, 'IsDecomposedBy'):
            for rel in element.IsDecomposedBy:
                for child in rel.RelatedObjects:
                    node['children'].append(self._get_spatial_node(child))
        
        # Processar espaços contidos
        if hasattr(element, 'ContainsElements'):
            for rel in element.ContainsElements:
                for contained in rel.RelatedElements:
                    node['children'].append({
                        'id': contained.id(),
                        'global_id': contained.GlobalId,
                        'name': contained.Name or f'{contained.is_a()}_{contained.id()}',
                        'type': contained.is_a(),
                        'children': []
                    })
        
        return node
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do modelo IFC.
        
        Returns:
            dict: Estatísticas (total de elementos, tipos, etc.)
        """
        if not self.model:
            return {}
        
        element_types = {}
        total_with_geometry = 0
        
        for element in self.model.by_type("IfcProduct"):
            element_type = element.is_a()
            element_types[element_type] = element_types.get(element_type, 0) + 1
            
            # Verificar se tem geometria
            if hasattr(element, 'Representation') and element.Representation:
                total_with_geometry += 1
        
        return {
            'total_elements': len(self.model.by_type("IfcProduct")),
            'total_with_geometry': total_with_geometry,
            'elements_by_type': dict(sorted(element_types.items(), key=lambda x: x[1], reverse=True)),
            'total_types': len(element_types),
            'schema': self.model.schema,
            'total_properties': len(self.model.by_type("IfcPropertySet"))
        }
    
    def get_element_by_global_id(self, global_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca elemento por GlobalId.
        
        Args:
            global_id: Global ID do elemento IFC
            
        Returns:
            dict: Dados do elemento ou None se não encontrado
        """
        if not self.model:
            return None
        
        try:
            element = self.model.by_guid(global_id)
            return self.get_element_properties(element.id())
        except Exception as e:
            logger.error(f"Erro ao buscar elemento {global_id}: {e}")
            return None
    
    def search_elements_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Busca elementos por nome (case-insensitive).
        
        Args:
            name: Nome ou parte do nome para buscar
            
        Returns:
            list: Lista de elementos encontrados
        """
        if not self.model:
            return []
        
        results = []
        name_lower = name.lower()
        
        for element in self.model.by_type("IfcProduct"):
            if element.Name and name_lower in element.Name.lower():
                results.append({
                    'id': element.id(),
                    'global_id': element.GlobalId,
                    'name': element.Name,
                    'type': element.is_a(),
                    'description': element.Description or ''
                })
        
        return results
    
    def get_bounds(self) -> Optional[Dict[str, Any]]:
        """
        Calcula os limites (bounding box) do modelo.
        
        Returns:
            dict: Coordenadas min/max do modelo ou None se erro
        """
        if not self.model:
            return None
        
        try:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            
            min_x = min_y = min_z = float('inf')
            max_x = max_y = max_z = float('-inf')
            
            for product in self.model.by_type("IfcProduct"):
                if not product.Representation:
                    continue
                
                try:
                    shape = ifcopenshell.geom.create_shape(settings, product)
                    verts = shape.geometry.verts
                    
                    for i in range(0, len(verts), 3):
                        x, y, z = verts[i], verts[i+1], verts[i+2]
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        min_z = min(min_z, z)
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)
                        max_z = max(max_z, z)
                except:
                    continue
            
            if min_x == float('inf'):
                return None
            
            return {
                'min': {'x': min_x, 'y': min_y, 'z': min_z},
                'max': {'x': max_x, 'y': max_y, 'z': max_z},
                'center': {
                    'x': (min_x + max_x) / 2,
                    'y': (min_y + max_y) / 2,
                    'z': (min_z + max_z) / 2
                },
                'size': {
                    'x': max_x - min_x,
                    'y': max_y - min_y,
                    'z': max_z - min_z
                }
            }
        except Exception as e:
            logger.error(f"Erro ao calcular bounds: {e}")
            return None
    
    def get_spaces_with_coordinates(self) -> List[Dict[str, Any]]:
        """
        Extrai espaços IFC com suas coordenadas para visualização de planta baixa.
        
        Returns:
            list: Lista de espaços com coordenadas X, Y, Z, área, volume, etc.
        """
        if not self.model:
            return []
        
        try:
            spaces = self.model.by_type("IfcSpace")
            spaces_data = []
            
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            
            for space in spaces:
                space_info = {
                    'id': space.id(),
                    'global_id': space.GlobalId,
                    'name': space.Name or f'Space_{space.id()}',
                    'long_name': space.LongName if hasattr(space, 'LongName') else '',
                    'description': space.Description or '',
                    'object_type': space.ObjectType if hasattr(space, 'ObjectType') else '',
                    'x_coordinate': 0.0,
                    'y_coordinate': 0.0,
                    'z_coordinate': 0.0,
                    'area': 0.0,
                    'volume': 0.0,
                    'height': 0.0
                }
                
                # Extrair coordenadas do placement
                try:
                    if hasattr(space, 'ObjectPlacement') and space.ObjectPlacement:
                        placement = space.ObjectPlacement
                        if hasattr(placement, 'RelativePlacement'):
                            rel_placement = placement.RelativePlacement
                            if hasattr(rel_placement, 'Location'):
                                location = rel_placement.Location
                                if hasattr(location, 'Coordinates'):
                                    coords = location.Coordinates
                                    if len(coords) >= 3:
                                        space_info['x_coordinate'] = float(coords[0])
                                        space_info['y_coordinate'] = float(coords[1])
                                        space_info['z_coordinate'] = float(coords[2])
                except Exception as e:
                    logger.warning(f"Erro ao extrair coordenadas do espaço {space.id()}: {e}")
                
                # Extrair propriedades quantitativas
                try:
                    if hasattr(space, 'IsDefinedBy'):
                        for definition in space.IsDefinedBy:
                            if definition.is_a('IfcRelDefinesByProperties'):
                                property_set = definition.RelatingPropertyDefinition
                                
                                # Verificar se é um QuantitySet
                                if property_set.is_a('IfcElementQuantity'):
                                    for quantity in property_set.Quantities:
                                        quantity_name = quantity.Name.lower()
                                        
                                        if 'area' in quantity_name or quantity_name == 'netfloorarea':
                                            if hasattr(quantity, 'AreaValue'):
                                                space_info['area'] = float(quantity.AreaValue)
                                        elif 'volume' in quantity_name or quantity_name == 'grossvolume':
                                            if hasattr(quantity, 'VolumeValue'):
                                                space_info['volume'] = float(quantity.VolumeValue)
                                        elif 'height' in quantity_name:
                                            if hasattr(quantity, 'LengthValue'):
                                                space_info['height'] = float(quantity.LengthValue)
                except Exception as e:
                    logger.warning(f"Erro ao extrair quantidades do espaço {space.id()}: {e}")
                
                # Se não conseguiu extrair área, tentar calcular da geometria
                if space_info['area'] == 0.0 and space.Representation:
                    try:
                        shape = ifcopenshell.geom.create_shape(settings, space)
                        # Estimativa simples de área baseada no bounding box
                        verts = shape.geometry.verts
                        if len(verts) >= 3:
                            min_x = min_y = float('inf')
                            max_x = max_y = float('-inf')
                            for i in range(0, len(verts), 3):
                                x, y = verts[i], verts[i+1]
                                min_x = min(min_x, x)
                                min_y = min(min_y, y)
                                max_x = max(max_x, x)
                                max_y = max(max_y, y)
                            space_info['area'] = (max_x - min_x) * (max_y - min_y)
                    except Exception as e:
                        logger.warning(f"Erro ao calcular área da geometria: {e}")
                
                spaces_data.append(space_info)
            
            logger.info(f"Extraídos {len(spaces_data)} espaços com coordenadas")
            return spaces_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair espaços com coordenadas: {e}")
            return []

