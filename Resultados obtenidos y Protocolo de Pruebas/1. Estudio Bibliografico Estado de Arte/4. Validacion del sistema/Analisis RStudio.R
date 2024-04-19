#Se extraen los datos recolectados del Diseño factorial
Resultados_Analisis_DisenoFactorial


# Realiza un ANOVA utilizando el modelo lineal general (GLM) para la respuesta ErrorBioflo, evaluando los 
# efectos principales y las interacciones de los factores Temperatura, Agitación y Aireación. 
# Los datos provienen de Resultados_Analisis_DisenoFactorial.
biorreactor.aov<-aov(ErrorBioflo~ Temperatura*Agitacion*Aireacion, data=Resultados_Analisis_DisenoFactorial)

biorreactor.aov #Imprime el objeto biorreactor.aov, que contiene los resultados del ANOVA.

# Proporciona un resumen detallado del ANOVA, incluyendo las estadísticas de 
# significancia para los efectos principales y las interacciones.
summary(biorreactor.aov)

#Genera gráficos diagnósticos del ajuste del modelo ANOVA para evaluar suposiciones como normalidad y homogeneidad de varianzas.
plot(biorreactor.aov) 

residuales<-resid(biorreactor.aov) #Calcula los residuales del modelo ANOVA y los almacena en residuales.
residuales #Imprime los valores residuales calculados.

# Asegurar que los paquetes necesarios estén instaladoss
if (!requireNamespace("car", quietly = TRUE)) {
  install.packages("car")
}

library(car) #Carga la biblioteca car, utilizada para pruebas estadísticas adicionales como la prueba de Levene.

# Hace que las columnas del dataframe Resultados_Analisis_DisenoFactorial
# estén disponibles como variables en el espacio de trabajo de R. 
# Esto facilita su uso en funciones subsecuentes sin necesidad de especificar el dataframe.
attach(Resultados_Analisis_DisenoFactorial) 

# Realiza la prueba de Levene para evaluar la homogeneidad de las varianzas de los
# residuales para cada uno de los factores Temperatura, Agitación y Aireación.
leveneTest(residuales, Temperatura)
leveneTest(residuales, Agitacion)
leveneTest(residuales, Aireacion)


shapiro.test(residuales) #Realiza la prueba de Shapiro-Wilk para evaluar la normalidad de los residuales del modelo.


# Asegurar que los paquetes necesarios estén instalados
if (!requireNamespace("lmtest", quietly = TRUE)) {
  install.packages("lmtest")
}
library(lmtest) #Carga la biblioteca lmtest, utilizada para realizar pruebas estadísticas sobre modelos lineales
dwtest(biorreactor.aov) #Realiza la prueba de Durbin-Watson para detectar autocorrelación en los residuales del modelo ANOVA.


# Asegurar que los paquetes necesarios estén instalados
if (!requireNamespace("agricolae", quietly = TRUE)) {
  install.packages("agricolae")
}
library(agricolae) #Carga la biblioteca agricolae, utilizada para análisis estadísticos en agricultura, incluyendo pruebas post-hoc


# Realiza la prueba post-hoc de Tukey para comparaciones múltiples de medias
# entre los niveles de cada factor (Temperatura, Agitación, Aireación), y almacena los resultados.
Tukey<-HSD.test(biorreactor.aov, "Temperatura")
Tukey
Tukey2<-HSD.test(biorreactor.aov, "Agitacion")
Tukey2
Tukey3<-HSD.test(biorreactor.aov, "Aireacion")
Tukey3

# Asegurar que los paquetes necesarios estén instalados
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  install.packages("ggplot2")
}
if (!requireNamespace("openxlsx", quietly = TRUE)) {
  install.packages("openxlsx")
}

# Cargar el paquete ggplot2
library(ggplot2)
library(openxlsx)


# Extraer la tabla de análisis de varianza para el objeto biorreactor.aov
anova_table <- summary(biorreactor.aov)[[1]]

# Eliminar la última fila de la tabla ANOVA, asumiendo que es "Residuals"
anova_table <- anova_table[-nrow(anova_table), ]

# Excluir la fila "Residuals" de la tabla ANOVA
# Asegúrate de que este paso se realiza antes de calcular los efectos estandarizados
residuals_row_index <- which(row.names(anova_table) == "Residuals")
if (length(residuals_row_index) > 0) {
  anova_table <- anova_table[-residuals_row_index, ]
}

# Calcular los efectos estandarizados sin incluir "Residuals"
anova_table$EfectoEstandarizado <- sqrt(anova_table$"Mean Sq")

# Crear un dataframe con los efectos y sus efectos estandarizados
efectos_estandarizados <- data.frame(
  Efecto = row.names(anova_table),
  EfectoEstandarizado = anova_table$EfectoEstandarizado
)

# Ordenar los efectos por su magnitud estandarizada de forma descendente para el gráfico de Pareto
efectos_estandarizados <- efectos_estandarizados[order(-efectos_estandarizados$EfectoEstandarizado),]

# Generar el gráfico de Pareto
ggplot(efectos_estandarizados, aes(x=reorder(Efecto, EfectoEstandarizado), y=EfectoEstandarizado)) +
  geom_bar(stat="identity", fill="skyblue") +
  theme(axis.text.x = element_text(angle=65, hjust=1)) +
  labs(x="Efecto", y="Efecto Estandarizado", title="Gráfico de Pareto de Efectos Estandarizados")

# Escribe el dataframe de efectos estandarizados a un archivo Excel.
write.xlsx(efectos_estandarizados, file = "Resultados_Efectos_Estandarizados.xlsx", sheetName = "Efectos Estandarizados", rowNames = FALSE)
