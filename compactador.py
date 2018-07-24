import re
import struct
import lzma
import time
import sys

def lzma_compact(img,cabecalho,saida):
    '''o uso do lzma é opcional por que é uma biblioteca importada
    no meu teste com lzma, ele compacta 98~99% do arquivo'''
    img=list(img)

    #descobre o tamanho para empacotar
    x=str(len(img))+'B'

    #empacota tudo
    img=struct.pack(x,*img)
    with open(saida, "wb") as f:
        #escreve o cabeçalho sem o lzma
        f.write(cabecalho)
        with lzma.open(f, "w") as lzf:
            #compacta com o lzma
            lzf.write(img)
    f.close()




def comp(entrada, saida,algoritmo="lzw",tam=16):
    ''' se o algoritmo for o tar ele faz algo semelhante ao tarball
        se o lzma for verdadeiro ele usa o Algoritmo de
        Lempel-Ziv-Markov
        com o tarball, consegui reduzir de 10.7mb para 3mb
        (72% de comprensão)
        com o lzma, consegui reduzir para 103kb (99% de comprensão)
        e com o lzw puro aumentou os 3mb para 4,3mb e com o lzw por
        cor diminui para 1.2mb


    '''
    tam=2**tam


    if tam<=65536:
        flag='H'
    elif tam <=4294967296:
        flag='I'
    else:
        raise ValueError("Tamango não pode ser maior que 4294967296, por enquanto")

    f=open(entrada,'r')
    #le o tipo do dado ex: P3 e coloca na forma de bits
    tipo=f.readline().encode()
    #le as dimensoes e coloca em uma lista como inteiro
    dim=list(map(int,f.readline().split(" ")))
    #le o valor maximo
    inter=int(f.readline())

    #empacota os valores do cabecalho e coloca uma quebra de linha como separador
    cabecalho=struct.pack('2s 3I c',tipo,dim[0],dim[1],inter,b'\n')

    #separa em uma lista tudo o que possui uma quebra de linha ou espaço, removendo o lixo do final
    img=(map(int,re.split('\n| ',f.read()[0:-1])))


    if algoritmo=="lzma":
        #salva com o lzma
        lzma_compact(img,cabecalho,saida)
        return
    elif algoritmo=="lzw":

        img=lzw_comp(img,cabecalho,tam)
        f= open(saida,'wb')
        f.write(cabecalho)
        for i in img:
            f.write(struct.pack('I',i))

    elif algoritmo=='tar':
        f= open(saida,'wb')
        f.write(cabecalho)
        for i in img:
            f.write(struct.pack('B',i))
    elif algoritmo=='lzw_':
        f= open(saida,'wb')
        f.write(cabecalho)
        red=[]
        gray=[]
        blue=[]
        for i in map(int,img):
            red.append(i)
            gray.append(next(img))
            blue.append(next(img))


        red=lzw_comp(red,cabecalho,tam)
        gray=lzw_comp(gray,cabecalho,tam)
        blue=lzw_comp(blue,cabecalho,tam)
        for i in red:
            f.write(struct.pack(flag,i))
        f.write(struct.pack(flag,256))
        for i in gray:
            f.write(struct.pack(flag,i))
        f.write(struct.pack(flag,256))
        for i in blue:
            f.write(struct.pack(flag,i))

    else:


        raise  ValueError("Escolha entre lzma, lzw ou tar")

    f.close()

def lzw_comp(img,cabecalho,tam):
    '''aumentou aquele arquivo para 4,3mb, apenas aplicando
    mas se for usado para cada cor o arquivo vai para 1.2mb'''
    img=[chr(i) for i in img]



    dicionario_palavras={}

    resultado=[]

    for i in range(256):
        dicionario_palavras[chr(i)]=i


    cont=257
    tamanho_img=len(img) #evita chamada de função toda hora
    v=0


    j=0

    while(j<tamanho_img):
        i=img[j]
        if(j+1<tamanho_img):
            #vai juntado enquanto tem no dicionario
            while ((i+img[j+1]) in dicionario_palavras.keys()):
                i+=img[j+1]
                j+=1
                if(j+1==tamanho_img):
                    resultado.append(dicionario_palavras[i])
                    return resultado
        else:

            resultado.append(dicionario_palavras[i])
            return resultado

        resultado.append(dicionario_palavras[i])

        #vai adicionando no dicionario enquanto n passar pode tamanho limite
        if(cont<tam):
            dicionario_palavras[i+img[j+1]]=cont

            cont+=1


        j+=1





    return resultado

def debug_dict(dicionario_palavras):
    for i, j in zip (dicionario_palavras.keys(), dicionario_palavras.items()):
        if i>255:
            print (j)





def formata(f,img):
    '''solução feia para deixar no formato antigo,
    poderia ser substituido por f.write(i),
    mas não ficaria no mesmo formato'''
    cont=0
    for i in img:

        if i==' ':
            cont+=1
        if cont==3:
            f.writelines('\n')
            cont=0
        else:
            f.write(i)
def divide_tudo(lista_val):

    return [ord(i) for i in lista_val]
def lzw_descomp(crip,algoritmo,tam):
    '''camada mais externa do lzw'''
    resultado=[]
    if tam <=65536:
        crip=struct.iter_unpack("H",crip)
    else:
        crip=struct.iter_unpack("I",crip)
        #descompacta tudo
    if algoritmo=='lzw':

        w=chr(next(crip)[0])
        resultado.append(w)
        resultado=lzw_descomp_interno(crip,w,resultado,tam)
        resultado_normalizado=map(divide_tudo,resultado)

        resultado=[]
        for i in resultado_normalizado:
            for j in i:

                resultado.append(j)

        return resultado


    elif algoritmo=='lzw_':
        '''versão  do lzw para imagens que aplica o algortmo por cada cor'''
        red=[]
        gray=[]
        blue=[]


        #pega o primeiro valor do vermelho
        w=chr(next(crip)[0])
        resultado=[w]

        #enquando o valor n fica igual de 256
        #significa que ainda não mudou de cor
        for i in crip:
            if i[0]!=256:
                red.append(i)
            else:
                break
        red=lzw_descomp_interno(red,w,resultado,tam)
        w=chr(next(crip)[0])
        resultado=[w]


        for i in crip:
            if i[0]!=256:
                gray.append(i)
            else:
                break


        gray=lzw_descomp_interno(gray,w,resultado,tam)
        w=chr(next(crip)[0])
        resultado=[w]

        for i in crip:
            blue.append(i)


        blue=lzw_descomp_interno(blue,w,resultado,tam)

        red=map(divide_tudo,red)
        gray=map(divide_tudo,gray)
        blue=map(divide_tudo,blue)

        #pega todos elementos

        red=[j for i in red for j in i]
        gray=[j for i in gray for j in i]
        blue=[j for i in blue for j in i]

        resultado=[]
        for i,j,k in zip(red,gray,blue):

            resultado.append(i)
            resultado.append(j)
            resultado.append(k)


        return resultado









def lzw_descomp_interno(crip,w,resultado,tam=65536):
    '''descompactador mais interna, apenas aplica o método do lzw'''
    dicionario_palavras={}


    for i in range(256):
        dicionario_palavras[i]=chr(i)


    cont=257


    for i in crip:
        i=i[0]


        if (i in dicionario_palavras.keys()):
            #se tiver no dicionario, apenas adiciona
            entrada=dicionario_palavras[i]

        elif(i==cont):
            #se não tiver, mas i for igual ao contador, então este seria o proximo
            #valor a ser adicionado, (já aproveite e coloca na entrada)
            entrada = w+w[0]
        else:
            print("erro")
        resultado.append(entrada)

        dicionario_palavras[cont]=w+entrada[0]
        cont+=1
        w=entrada


    return resultado







def descomp(entrada,saida,algoritmo="lzw",formato=True,tam=16):
    '''descompacta o valor
        caso tenha sido compactado com use_lzma, aqui também deve
        ser usado o use_lzma
        caso não tenha sido usado, ele não pode ser considerado
        como verdadeiro
    '''
    tam=2**tam
    if tam>4294967296:
        raise ValueError("Por enquanto valor não pode ser maior que 4294967296")

    #abre arquivo em modo leitura de bits
    f=open(entrada,'rb')
    #le o cabeçalho
    cabecalho=struct.unpack('2s 3I c',f.readline())
    #le o resto
    #se estiver usando o lzma, ele descompacta e depois le
    if algoritmo=='lzma':
        crip=lzma.decompress(f.read())


    elif algoritmo=='lzw' or algoritmo=='lzw_':
        crip=f.read()
        crip=lzw_descomp(crip,algoritmo,tam)
    elif algoritmo =='tar':
        crip = f.read()

    else:
        raise  ValueError("Escolha entre lzma, lzw ou tar")


    f.close()

    #transforma os valores inteiros em string,
    #transforma a lista de string em um map
    #transforma tudo o que estava na lista em um string
    #separada por espaço

    img=' '.join(map(str,[i for i in crip]))




    f=open(saida,'w')
    #escreve cabecalho
    f.write(cabecalho[0].decode()+"\n"+str(cabecalho[1])+" "+str(cabecalho[2])+'\n'+str(cabecalho[3])+"\n")
    #caso formato seja verdadeiro, ele salva como o formato original, com cada 3 valores
    #separados por uma quebra de linha, caso contrário, salva tudo em uma linha só
    if formato:
        formata(f,img)
    else:
        f.write(img)

    f.close()


if __name__=="__main__":
    if sys.argv[1]=='-h':
        print ("\n\ndigite c para comprimir, d para descomprimir")
        print("arquivo de entrada, aquivo de saída, algortimo (escolha entre:")
        print("tar, lzw, lzw_ e lzma)")
        print ("o lzw_ é o mesmo lzw, porém compacta por cor")
        print(", exemplo de execução:")
        print("python compactador.py c entrada.ppm saida.tar lzw_ 32 (melhor resultado feito por mim)\n\n")

    if len(sys.argv)==5:
        sys.argv.append(32)


    if sys.argv[1]=='c':
        comp (sys.argv[2],sys.argv[3],algoritmo=sys.argv[4],tam=int(sys.argv[5]))
    elif sys.argv[1]=='d':
        descomp (sys.argv[2],sys.argv[3],algoritmo=sys.argv[4],tam=int(sys.argv[5]))
