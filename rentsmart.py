import csv
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

TAXA_CONTRATUAL = Decimal("2000.00")
MAX_PARCELAS = 5
MESES_PROJECAO = 12


def dinheiro(valor):
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def moeda(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class Imovel(ABC):
    nome = ""
    aluguel_base = Decimal("0")

    @abstractmethod
    def adicionais(self):
        pass

    def descricao(self):
        return self.nome

    def desconto(self, subtotal):
        return Decimal("0.00"), ""

    def itens_aluguel(self):
        return [(f"Aluguel-base ({self.nome})", self.aluguel_base)] + self.adicionais()


class Apartamento(Imovel):
    nome = "Apartamento"
    aluguel_base = Decimal("700.00")
    ADICIONAL_2_QUARTOS = Decimal("200.00")
    VAGA_GARAGEM = Decimal("300.00")
    DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos, garagem, tem_criancas):
        self.quartos = quartos
        self.garagem = garagem
        self.tem_criancas = tem_criancas

    def descricao(self):
        return f"{self.nome} de {self.quartos} quarto(s)"

    def adicionais(self):
        itens = []
        if self.quartos == 2:
            itens.append(("Adicional de 2 quartos", self.ADICIONAL_2_QUARTOS))
        if self.garagem:
            itens.append(("Vaga de garagem", self.VAGA_GARAGEM))
        return itens

    def desconto(self, subtotal):
        if not self.tem_criancas:
            valor = dinheiro(subtotal * self.DESCONTO_SEM_CRIANCAS)
            return valor, "Desconto de 5% (sem crianças)"
        return super().desconto(subtotal)


class Casa(Imovel):
    nome = "Casa"
    aluguel_base = Decimal("900.00")
    ADICIONAL_2_QUARTOS = Decimal("250.00")
    VAGA_GARAGEM = Decimal("300.00")

    def __init__(self, quartos, garagem):
        self.quartos = quartos
        self.garagem = garagem

    def descricao(self):
        return f"{self.nome} de {self.quartos} quarto(s)"

    def adicionais(self):
        itens = []
        if self.quartos == 2:
            itens.append(("Adicional de 2 quartos", self.ADICIONAL_2_QUARTOS))
        if self.garagem:
            itens.append(("Vaga de garagem", self.VAGA_GARAGEM))
        return itens


class Estudio(Imovel):
    nome = "Estúdio"
    aluguel_base = Decimal("1200.00")
    PACOTE_INICIAL_VAGAS = 2
    PACOTE_INICIAL_VALOR = Decimal("250.00")
    VAGA_ADICIONAL = Decimal("60.00")

    def __init__(self, vagas):
        self.vagas = vagas

    def adicionais(self):
        itens = []
        if self.vagas > 0:
            itens.append((f"Pacote de {self.PACOTE_INICIAL_VAGAS} vagas", self.PACOTE_INICIAL_VALOR))
            extras = self.vagas - self.PACOTE_INICIAL_VAGAS
            if extras > 0:
                itens.append((f"{extras} vaga(s) adicional(is) x {moeda(self.VAGA_ADICIONAL)}",
                              self.VAGA_ADICIONAL * extras))
        return itens


class Orcamento:

    def __init__(self, imovel, parcelas_taxa):
        self.imovel = imovel
        self.parcelas_taxa = parcelas_taxa
        self.itens = imovel.itens_aluguel()
        self.subtotal = sum((valor for _, valor in self.itens), Decimal("0.00"))
        self.desconto, self.motivo_desconto = imovel.desconto(self.subtotal)
        self.aluguel_mensal = dinheiro(self.subtotal - self.desconto)

    def parcelas(self):
        valor = dinheiro(TAXA_CONTRATUAL / self.parcelas_taxa)
        lista = [valor] * self.parcelas_taxa
        lista[-1] = TAXA_CONTRATUAL - valor * (self.parcelas_taxa - 1)
        return lista

    def projecao(self):
        parcelas = self.parcelas()
        linhas = []
        for mes in range(1, MESES_PROJECAO + 1):
            taxa = parcelas[mes - 1] if mes <= len(parcelas) else Decimal("0.00")
            linhas.append((mes, self.aluguel_mensal, taxa, self.aluguel_mensal + taxa))
        return linhas

    def resumo(self):
        parcelas = self.parcelas()
        linhas = ["", "=" * 52, "          RESUMO DO ORÇAMENTO - R.M IMÓVEIS", "=" * 52,
                  f"Imóvel: {self.imovel.descricao()}", "", "ALUGUEL MENSAL"]
        for descricao, valor in self.itens:
            linhas.append(f"  {descricao:<34}{moeda(valor):>16}")
        linhas.append(f"  {'Subtotal':<34}{moeda(self.subtotal):>16}")
        if self.desconto > 0:
            linhas.append(f"  {self.motivo_desconto:<34}{'- ' + moeda(self.desconto):>16}")
        linhas.append(f"  {'VALOR MENSAL DO ALUGUEL':<34}{moeda(self.aluguel_mensal):>16}")
        linhas += ["", "TAXA CONTRATUAL (cobrada à parte do aluguel)",
                   f"  {'Valor total':<34}{moeda(TAXA_CONTRATUAL):>16}",
                   f"  Parcelamento: {self.parcelas_taxa}x de {moeda(parcelas[0])}"]
        if parcelas[-1] != parcelas[0]:
            linhas.append(f"  (última parcela: {moeda(parcelas[-1])})")
        total_ano = sum(total for *_, total in self.projecao())
        linhas += ["", f"Total previsto nos 12 primeiros meses: {moeda(total_ano)}", "=" * 52]
        return "\n".join(linhas)

    def exportar_csv(self, caminho="projecao_12_meses.csv"):
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mês", "Aluguel (R$)", "Parcela da taxa (R$)", "Total do mês (R$)"])
            for mes, aluguel, taxa, total in self.projecao():
                escritor.writerow([mes] + [str(v).replace(".", ",") for v in (aluguel, taxa, total)])
            total_ano = sum(total for *_, total in self.projecao())
            escritor.writerow(["TOTAL", "", "", str(total_ano).replace(".", ",")])
        return caminho


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print(f"  Entrada inválida. Digite um número entre {minimo} e {maximo}.")


def ler_sim_nao(mensagem):
    while True:
        texto = input(mensagem + " (s/n): ").strip().lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        print("  Entrada inválida. Digite 's' ou 'n'.")


def montar_imovel():
    print("Tipo de imóvel:\n  1 - Apartamento\n  2 - Casa\n  3 - Estúdio")
    tipo = ler_inteiro("Escolha: ", 1, 3)

    if tipo == 3:
        vagas = ler_inteiro("Quantas vagas de estacionamento (0 a 10)? ", 0, 10)
        return Estudio(vagas)

    quartos = ler_inteiro("Número de quartos (1 ou 2): ", 1, 2)
    garagem = ler_sim_nao("Deseja vaga de garagem?")
    if tipo == 1:
        tem_criancas = ler_sim_nao("Possui crianças?")
        return Apartamento(quartos, garagem, tem_criancas)
    return Casa(quartos, garagem)


def main():
    print("=== RentSmart | R.M Imóveis ===\n")
    imovel = montar_imovel()
    parcelas = ler_inteiro(f"Parcelar a taxa contratual em quantas vezes (1 a {MAX_PARCELAS})? ",
                           1, MAX_PARCELAS)
    orcamento = Orcamento(imovel, parcelas)
    print(orcamento.resumo())
    caminho = orcamento.exportar_csv()
    print(f"\nProjeção de 12 meses salva em: {caminho}")


if __name__ == "__main__":
    main()
