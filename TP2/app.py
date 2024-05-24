from generator import uniform, exponential, normal
from plot import plot_distribution
from fit import fit


def menu():
    n = -1
    distribution = ""
    intervals = 0
    nums = []
    lambd = 0
    mean = 0
    std = 0
    # Select the distribution
    while n != 0:
        n = int(input("Ingrese la cantidad de numeros a generar, o 0 para salir: "))
        if not (0 <= n <= 1000000):
            print("Solo se pueden ingresar valores positivos y menores a 1 millon.")
            continue
        elif n == 0: break
        print("1 - Uniforme")
        print("2 - Exponencial")
        print("3 - Normal")

        while distribution not in ["uniform", "exponential", "normal"]:
            distribution = input("Elija una distribucion: ")
            if distribution == "1": distribution = "uniform"
            elif distribution == "2": distribution = "exponential"
            elif distribution == "3": distribution = "normal"
            else: print("Distrubucion no disponible.")
        
        if distribution == "uniform":
            a = float(input("Ingrese el valor de A: "))
            b = float(input("Ingrese el valor de B: "))
            while a >= b:
                print("B debe ser mayor que A")
                b = float(input("Ingrese el valor de B: "))
            nums = uniform(a, b, n)
        elif distribution == "exponential":
            lambd = float(input("Ingrese el valor de Lambda: "))
            while lambd <= 0:
                print("Lambda debe ser mayor que cero!")
                lambd = float(input("Ingrese el valor de lambda: "))
            nums = exponential(lambd, n)
        else:
            mean = float(input("Ingrese la media: "))
            std = float(input("Ingrese la desviacion estandar: "))
            while mean < 0:
                print("La desviacion estandar debe ser mayor que cero!")
                mean = float(input("Ingrese la desviacion estandar: "))
            nums = normal(mean, std, n)

        # Get a list of all the random generated numbers
        nums = list(nums)
        intervals = int(input("Ingrese el numero de intervalos: "))
        while intervals not in [10, 12, 16, 23]:
            print("Solo se pueden los valores 10, 12, 16 y 23.")
            intervals = int(input("Ingrese el numero de intervalos: "))
        # Plot the distribution
        plot_distribution(nums, intervals)
        # Fit the distribution
        if distribution == "uniform":
            params = {"a": a, "b": b}
        if distribution == "exponential":
            params = {"lambd": lambd}
        else:
            params = {"mean": mean, "std": std}
        chisq_data, chisq_value, ks_data, ks_value = fit(distribution, nums, intervals, params)
        print(chisq_data)
        print("Valor de chi cuadrado: ", chisq_value)
        print(ks_data)
        print("Valor de KS: ", ks_value)
        # Clear variables so the loop can continue
        distribution = ""
        intervals = 0



def main():
    menu()

if __name__ == '__main__':
    main()
