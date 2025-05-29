from shiny import App, ui, reactive, render
import pandas as pd

"""CALCULO DO SALÁRIO LIQUIDO"""


# calcular o desconto do INSS
def calcular_inss(salario_bruto):
    faixa_do_inss = [
        (1518.00, 0.075),
        (2793.88, 0.09),
        (4190.83, 0.12),
        (8157.41, 0.14)
    ]

    desconto = 0.0  #acumula o valor total do desconto do INSS.
    salario_restante = salario_bruto  #salário que ainda não foi processado
    limite_inf = 0.0  

    for limite_super, percentual in faixa_do_inss:      #Caso o salário seja maior que o limite, vai calcular o desconto daquela faixa.
        if salario_bruto > limite_super:                
            faixa = limite_super - limite_inf           
            desconto += faixa * percentual              
            limite_inf = limite_super                   #Se não, calcula o que falta e encerra.
        else:
            faixa = salario_restante - limite_inf
            desconto += faixa * percentual
            break

    return desconto

#calcular o desconto do IR
def calcular_ir(salario_base):
    faixas_ir = [
        (2259.20, 0.0, 0.0),
        (2826.65, 0.075, 169.44),
        (3751.05, 0.15, 381.44),
        (4664.68, 0.225, 662.77),
        (float('inf'), 0.275, 896.00)
    ]

    for limite_super, percentual, deducao in faixas_ir:
        if salario_base <= limite_super:
            return salario_base * percentual - deducao
    return 0.0


#Interface Gráfica
app_ui = ui.page_fluid(
    ui.h2("Calculadora de Salário Líquido", style=" text-align: center"),

    ui.layout_columns(
        ui.card(ui.h4("Salario"), ui.input_numeric("salario_bruto", "Salário Bruto (R$):", value=6000, min=0, step=100)),
        ui.card(ui.h4("Previdencia Privada"), ui.input_numeric("previdencia", "Previdencia Privada (R$):", value=0, min=0, step=10)),
        ui.card(ui.h4("Outros Gastos"), ui.input_numeric("outros_gastos", "Outros Gastos (R$):", value=0, min=0, step=10)),
        
    ),

    ui.card(
        ui.h4("Resultado",style=" text-align: center"),
        ui.output_data_frame("resultado")
    ),
    
)

# Servidor
def server(input, output, session):
    @reactive.calc  #Dependerá de outros valores para mudar
    def calcular():
        salario_bruto = input.salario_bruto()
        previdencia = input.previdencia()
        outros_gastos = input.outros_gastos()
        desconto_inss = calcular_inss(salario_bruto)
        salario_base_ir = salario_bruto - desconto_inss
        desconto_ir = calcular_ir(salario_base_ir)
        salario_liquido = salario_bruto - desconto_inss - desconto_ir - previdencia - outros_gastos
        total_desconto = desconto_inss + desconto_ir + previdencia + outros_gastos
        
        result=[]
        result.append({
        "Salário Bruto (R$)": round(salario_bruto, 2),
        "Desconto INSS (R$)": round(desconto_inss, 2),
        "Desconto IRRF (R$)": round(desconto_ir, 2),
        "Previdência Privada (R$)": round(previdencia, 2),
        "Outros Gastos (R$)": round(outros_gastos, 2),
        "Salário Líquido (R$)": round(salario_liquido, 2),
        "Total de Descontos (R$)": round(total_desconto, 2)
        })
        
        df = pd.DataFrame(result)
        return df
        
    #Saida
    @output
    @render.data_frame
    def resultado():
        
       return calcular()  
   
   
# Criação da aplicação
app = App(app_ui, server)