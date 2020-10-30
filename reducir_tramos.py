from osgeo import ogr, osr
"""
    Se va a extraer del shp los concellos de las comarcas de Galicia por los que pase el "Camino Francés"
	del Camino de Santiago: Arzúa, Santiago, Terra De Melide, A Ulloa, Lugo, Sarria, Os Ancares
"""

#Fichero de origen
fichero_origen = "shp/Concellos_IGN.shp"
#Lo abrimos con el data source de origen
data_source_origen = ogr.Open(fichero_origen)
#Recuperamos la capa del origen
capa_origen = data_source_origen.GetLayer()


#Preparamos el fichero /de destino/nuevo/a crear/
fichero_destino = "shp/concellos_camino_frances.shp"
#Creamos el data source de destino
data_source_destino = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(fichero_destino)
#Creamos la capa de destino, con la referencia espacial del fichero de origen
capa_destino = data_source_destino.CreateLayer("Concellos camino Frances",capa_origen.GetSpatialRef())

#A continuación, damos forma al molde.


#Un atributo con código de la provincia
esquema_atributo = ogr.FieldDefn("CodPROV", ogr.OFTString)
esquema_atributo.SetWidth(10)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el código de la comarca
esquema_atributo = ogr.FieldDefn("CodCOM", ogr.OFTString)
esquema_atributo.SetWidth(10)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el nombre de la comarca
esquema_atributo = ogr.FieldDefn("Comarca", ogr.OFTString)
esquema_atributo.SetWidth(30)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el nombre de la provincia
esquema_atributo = ogr.FieldDefn("Provincia", ogr.OFTString)
esquema_atributo.SetWidth(30)
capa_destino.CreateField(esquema_atributo)

#Un atributo con el código de la concello
esquema_atributo = ogr.FieldDefn("Concello", ogr.OFTString)
esquema_atributo.SetWidth(10)
capa_destino.CreateField(esquema_atributo)


"""
    A partir de aquí, iteramos por las features de origen, y volcamos aquellas
    que cumplen la condición
"""
capa_destino_esquema = capa_destino.GetLayerDefn()
feature_origen = capa_origen.GetNextFeature()
while feature_origen:
    if (feature_origen.GetField("Comarca") == "Santiago") or (feature_origen.GetField("Comarca") == "Arzúa") or (feature_origen.GetField("Comarca") == "Terra De Melide") or (feature_origen.GetField("Comarca") == "A Ulloa") or (feature_origen.GetField("Comarca") == "Lugo") or (feature_origen.GetField("Comarca") == "Sarria") or (feature_origen.GetField("Comarca") == "Os Ancares"):
        #Creamos la feature de destino
        feature_destino = ogr.Feature(capa_destino_esquema)
        #Establecemos la geometría
        feature_destino.SetGeometry(feature_origen.GetGeometryRef())
        #Rellenamos los atributos
        feature_destino.SetField("CodPROV",feature_origen.GetField("CodPROV"))
        feature_destino.SetField("CodCOM",feature_origen.GetField("CodCOM"))
        feature_destino.SetField("Provincia",feature_origen.GetField("Provincia"))
        feature_destino.SetField("Comarca",feature_origen.GetField("Comarca"))
        feature_destino.SetField("Concello",feature_origen.GetField("Concello"))

        #Volcamos a la capa
        capa_destino.CreateFeature(feature_destino)
        #Limpiamos referencia
        feature_destino = None

    #Actualizamos la feature de origen
    feature_origen = capa_origen.GetNextFeature()

#Una vez acabado el bucle, liberamos los data sources

data_source_destino = None
data_source_origen = None