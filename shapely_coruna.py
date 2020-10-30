from osgeo import ogr, osr
"""
	Se van a extraer concellos de las comarcas de Galicia por los que pase el "Camino Francés"
	del Camino de Santiago en la provincia de Coruña

"""
import shapely.wkt


#Fichero de origen Concellos
fichero_concellos = "shp/concellos_camino_frances.shp"
#Lo abrimos con el data source de origen
data_source_concellos = ogr.Open(fichero_concellos)
#Recuperamos la capa del origen
capa_concellos = data_source_concellos.GetLayer()


#Preparamos el fichero /de destino/nuevo/a crear/
fichero_destino = "shp/concellos_camino_frances_coruna.shp"
#Creamos el data source de destino
data_source_destino = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(fichero_destino)
#Creamos la capa de destino, con la referencia espacial del fichero de origen
capa_destino = data_source_destino.CreateLayer("Concellos camino Frances",capa_concellos.GetSpatialRef())


#Y su molde
#Un atributo con código de la provincia
esquema_atributo = ogr.FieldDefn("CodPROV", ogr.OFTString)
esquema_atributo.SetWidth(50)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el código de la comarca
esquema_atributo = ogr.FieldDefn("CodCOM", ogr.OFTString)
esquema_atributo.SetWidth(50)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el nombre de la comarca
esquema_atributo = ogr.FieldDefn("Comarca", ogr.OFTString)
esquema_atributo.SetWidth(50)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el nombre de la provincia
esquema_atributo = ogr.FieldDefn("Provincia", ogr.OFTString)
esquema_atributo.SetWidth(50)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el nombre del concello
esquema_atributo = ogr.FieldDefn("Concello", ogr.OFTString)
esquema_atributo.SetWidth(50)
capa_destino.CreateField(esquema_atributo)


#Fichero de origen Provincias
fichero_provincias = "shp/Provincias_IGN.shp"
#Lo abrimos con el data source de origen
data_source_provincias = ogr.Open(fichero_provincias)
#Recuperamos la capa del origen
capa_provincias = data_source_provincias.GetLayer()

#Vamos a buscar la geometría de Coruña
geometria_coruna = None

feature_provincia = capa_provincias.GetNextFeature()
while feature_provincia:
    #¿Es Coruña?
    if feature_provincia.GetField("Provincia") == "A Coruña":
        #Guardamos la geometría
        geometria_coruna = feature_provincia.GetGeometryRef().Clone()
    #Actualizamos la feature de origen
    feature_provincia = capa_provincias.GetNextFeature()
#Liberamos el data source de provincias
data_source_provincias = None

#Ahora recorremos el SHP de los concellos y volcamos en los que estén en Coruña
capa_destino_esquema = capa_destino.GetLayerDefn()
feature_concello = capa_concellos.GetNextFeature()

while feature_concello:
    """
        ¿Está la geometría de los concellos en A Coruña?
        Tenemos que comprobarlo con Shapely
        PERO
        Shapely funciona sobre un plano, es decir 2D.
        Así que habrá que pasar las geometrías a una proyección 2D
        (Porque WGS84 trabaja con longitudes y latitudes).

        Obviamente, la geometría de Coruña la podíamos (y debíamos) haber
        transformado fuera del bucle. También parte del código que le sigue.
        Se hace aquí dentro para explicar mejor el ejemplo de Shapely.
    """
    #EPSG:3035 Proyección 2D útil para Europa.
    referencia_espacial_2D = osr.SpatialReference()
    referencia_espacial_2D.ImportFromEPSG(3035)

    #Transformamos la geometría de Coruña
    transformacion = osr.CoordinateTransformation(geometria_coruna.GetSpatialReference(), referencia_espacial_2D)
    geometria_coruna.Transform(transformacion)


    #Ahora hacemos lo mismo con la feature del concello actual.
    #Nótese que se vuelve a hacer la transformación debido a que el fichero
    #de provincias podría haber una proyección diferente a la de los concellos
    geometria_concello = feature_concello.GetGeometryRef().Clone()
    referencia_espacial_concello = geometria_concello.GetSpatialReference()
    transformacion = osr.CoordinateTransformation(referencia_espacial_concello, referencia_espacial_2D)
    geometria_concello.Transform(transformacion)


    """
        En este momento, tenemos las geometrías de Coruña y el concello actual
        proyectadas en un plano 2D.
        Shapely y OGR pueden interoperar si convertimos las geometrías a WKT
    """
    geometria_coruna_shapely = shapely.wkt.loads(geometria_coruna.ExportToWkt())
    geometria_concello_shapely = shapely.wkt.loads(geometria_concello.ExportToWkt())

    #¿Contiene Asturias al río?
    if geometria_coruna_shapely.contains(geometria_concello_shapely):
        #Entonces volcamos
        #Creamos la feature de destino
        feature_destino = ogr.Feature(capa_destino_esquema)
        #La geometría en Shapely a WKT
        geometria_concello_wkt = shapely.wkt.dumps(geometria_concello_shapely)
        #El WKT lo pasamos a Geometría OGR
        geometria_destino = ogr.CreateGeometryFromWkt(geometria_concello_wkt)
        #Ahora tenemos la geometría pero en 2D, hay que deshacer la transformación
        transformacion = osr.CoordinateTransformation(referencia_espacial_2D,feature_concello.GetGeometryRef().GetSpatialReference())
        geometria_destino.Transform(transformacion)


        # Se convierte a EPSG 4326 para poder representar en el mapa
        # Spatial Reference System
        # Proyección UTM ED50 Huso 29 N
        inputEPSG = 32629
        # Coordenadas Geográficas WGS84
        outputEPSG = 4326
        # Creamos la transformacion de coordenadas
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(inputEPSG)
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(outputEPSG)
        coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        # Transformamos la geometria
        geometria_destino.Transform(coordTransform)
        #Ahora ya asignamos la geometría a la nueva feature
        feature_destino.SetGeometry(geometria_destino)

        #Rellenamos los atributos
        feature_destino.SetField("CodPROV",feature_concello.GetField("CodPROV"))
        feature_destino.SetField("CodCOM",feature_concello.GetField("CodCOM"))
        feature_destino.SetField("Provincia",feature_concello.GetField("Provincia"))
        feature_destino.SetField("Comarca",feature_concello.GetField("Comarca"))
        feature_destino.SetField("Concello",feature_concello.GetField("Concello"))

        #Volcamos a la capa
        capa_destino.CreateFeature(feature_destino)
        #Limpiamos referencia
        feature_destino = None

    #Actualizamos la feature de origen
    feature_concello = capa_concellos.GetNextFeature()

#Una vez acabado el bucle, liberamos los data sources
data_source_destino = None
data_source_provincias = None
data_source_concellos = None