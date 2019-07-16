import sys, os, socket

# FUNCOES USADAS
def usage():
    os.system("clear")
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print("ERRO\n")
        print("Usage: %s protocolo_que_vc_quer_farejar\n\nprotocolo_que_vc_quer_farejar = udp ou tcp ou ip\n" % sys.argv[0])
        sys.exit()
    if (sys.argv[1].lower() != 'tcp') and (sys.argv[1].lower() != 'udp') and (sys.argv[1].lower() != 'ip'):
        print("ERRO\n")
        print('Escreva como argumento uma forma valida de protocolo: udp, tcp ou ip')
        sys.exit()

#MAIN
def main():
    usage()
    print("Ola jovem hacker, bem vindo ao meu programa de sniffing\nIsso definitivamente nao eh ilegal\n")
    print("Iremos agora capturar pacotes", sys.argv[1])
    input("Pressione qualquer tecla para continuar")
    os.system('clear')
    print('Capturando pacotes ' + sys.argv[1] + '...')
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)  # socket.IPPROTO_IP

    while True:
        print(s.recvfrom(65565))

if __name__ == '__main__':
    main()