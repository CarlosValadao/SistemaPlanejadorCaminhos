import numpy as np
import matplotlib.pyplot as plt

def calcular_campo_potencial(grid_size, objetivo, obstaculos, alcance_repulsao, fator_atrativo=5.0, fator_repulsivo=25.0):
    """
    Calcula o campo potencial em uma grade.
    """
    linhas, colunas = grid_size
    campo = np.zeros((linhas, colunas))

    # Campo atrativo
    for x in range(linhas):
        for y in range(colunas):
            distancia = np.sqrt((x - objetivo[0])**2 + (y - objetivo[1])**2)
            campo[x, y] += fator_atrativo * distancia
    
    # Campo repulsivo
    for obstaculo in obstaculos:
        (x1, y1), (x2, y2) = obstaculo
        for x in range(linhas):
            for y in range(colunas):
                distancia = np.sqrt((x - (x1 + x2) / 2)**2 + (y - (y1 + y2) / 2)**2)
                if distancia < alcance_repulsao:
                    campo[x, y] += fator_repulsivo * (1.0 / distancia - 1.0 / alcance_repulsao)**2
    
    return campo

def calcular_orientacao(posicao_atual, proxima_posicao):
    """
    Calcula a orientação em graus entre duas posições.
    """
    dx = proxima_posicao[0] - posicao_atual[0]
    dy = proxima_posicao[1] - posicao_atual[1]
    angulo = np.degrees(np.arctan2(dy, dx))
    return (angulo + 360) % 360  # Ajusta para o intervalo [0, 360]

def planejar_trajetoria(campo, inicio, objetivo, max_passos=1000):
    trajeto = [(inicio[0], inicio[1])]
    posicao = inicio

    for _ in range(max_passos):
        #print(posicao)
        #print(objetivo)
        
        # Verifica se atingiu o objetivo
        if posicao == objetivo[0]:
            break  # Interrompe o loop ao atingir o objetivo
        
        x, y = posicao
        vizinhos = [
            (x - 1, y),  # Norte (90º)
            (x + 1, y),  # Sul (270º)
            (x, y - 1),  # Oeste (180º)
            (x, y + 1),  # Leste (0º)
        ]

        # Filtra vizinhos dentro do limite da grade
        vizinhos = [
            (vx, vy)
            for vx, vy in vizinhos
            if 0 <= vx < campo.shape[0] and 0 <= vy < campo.shape[1]
        ]
        
        # Calcula a próxima posição com base no campo potencial
        proxima_posicao = min(vizinhos, key=lambda p: campo[p])
        #orientacao = calcular_orientacao(posicao, proxima_posicao)

        if proxima_posicao[1] > 160/10  or proxima_posicao[1] < 20/10:
                break

        trajeto.append((proxima_posicao[0], proxima_posicao[1]))
        posicao = proxima_posicao
    
    return trajeto

'''
# Exemplo de uso
grid_size = (100, 100)
objetivo = (70, 20)
obstaculos = [[(20, 0), (40, 20)], [(60, 60), (70, 70)]]
inicio = (10, 10)

campo = calcular_campo_potencial(grid_size, objetivo, obstaculos, 10)
trajetoria = planejar_trajetoria(campo, inicio, objetivo)


# Visualização
plt.figure(figsize=(10, 10))
plt.imshow(campo.T, origin='lower', cmap='viridis', extent=[0, grid_size[0], 0, grid_size[1]])
plt.colorbar(label='Campo Potencial')

# Extrai x, y e orientações para visualização
trajetoria_x = [p[0] for p in trajetoria]
trajetoria_y = [p[1] for p in trajetoria]

plt.plot(trajetoria_x, trajetoria_y, 'r-', label='Trajetória')
plt.scatter([inicio[0], objetivo[0]], [inicio[1], objetivo[1]], color='white', label='Início/Objetivo')
for obs in obstaculos:
    (x1, y1), (x2, y2) = obs
    plt.gca().add_patch(plt.Rectangle((x1, y1), y2 - y1, x2 - x1, color='red', alpha=0.5, label='Obstáculo'))
plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Campo Potencial e Trajetória Planejada')
plt.grid(True)
plt.show()
'''
