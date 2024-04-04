Resultados_Analisis_DisenoFactorial
biorreactor.aov<-aov(ErrorBioflo~ Temperatura*Agitacion*Aireacion, data=Resultados_Analisis_DisenoFactorial)
biorreactor.aov
summary(biorreactor.aov)
plot(biorreactor.aov)
residuales<-resid(biorreactor.aov)
residuales
library(car)
attach(Resultados_Analisis_DisenoFactorial)
leveneTest(residuales, Temperatura)
leveneTest(residuales, Agitacion)
leveneTest(residuales, Aireacion)
shapiro.test(residuales)
library(lmtest)
dwtest(biorreactor.aov)


library(car)
library(agricolae)
Tukey<-HSD.test(biorreactor.aov, "Temperatura")
Tukey
Tukey2<-HSD.test(biorreactor.aov, "Agitacion")
Tukey2
Tukey3<-HSD.test(biorreactor.aov, "Aireacion")
Tukey3

