from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Incidente

def calcular_uptime_sistema(sistema, dias=30):
    agora = timezone.now()
    inicio = agora - timedelta(days=dias)

    incidentes = Incidente.objects.filter(
        sistema=sistema,
        data_criacao__gte=inicio
    ).exclude(status='Funcionando')

    total_periodo = (agora - inicio).total_seconds()
    tempo_indisponivel = 0

    for incidente in incidentes:
        fim = incidente.data_atualizacao if incidente.resolvido else agora
        comeco = max(incidente.data_criacao, inicio)
        tempo_indisponivel += (fim - comeco).total_seconds()

    uptime = ((total_periodo - tempo_indisponivel) / total_periodo) * 100
    return round(max(0, uptime), 2)


@login_required(login_url='/login/')
def index(request):
    incidentes = Incidente.objects.filter(resolvido=False).order_by('-data_criacao')

    for incidente in incidentes:
        incidente.uptime = calcular_uptime_sistema(incidente.sistema)

    return render(request, 'monitor/index.html', {'incidentes': incidentes})


def historico(request):
    incidentes_resolvidos = Incidente.objects.filter(resolvido=True).order_by('-data_criacao')
    return render(request, 'monitor/historico.html', {'incidentes': incidentes_resolvidos})


@login_required(login_url='/login/')
def registrar_incidente(request):
    if request.method == 'POST':
        sistema = request.POST.get('sistema')
        status = request.POST.get('status')
        descricao = request.POST.get('descricao')

        Incidente.objects.create(
            sistema=sistema,
            status=status,
            descricao=descricao,
            prioridade='media'
        )

        return redirect('index')

    return render(request, 'monitor/registrar_novo.html')


@login_required(login_url='/login/')
def incidentes_ativos(request):
    if request.method == 'POST':
        sistema_form = request.POST.get('sistema')
        status_form = request.POST.get('status')
        descricao_form = request.POST.get('descricao')

        novo_incidente = Incidente(
            sistema=sistema_form,
            status=status_form,
            descricao=descricao_form
        )
        novo_incidente.save()

        return redirect('index')

    return render(request, 'monitor/incidentes_ativos.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'monitor/login.html', {'form': {'errors': True}})

    return render(request, 'monitor/login.html')


@login_required(login_url='/login/')
def cadastro_view(request):
    if not request.user.is_superuser:
        return redirect('index')

    mensagem = None
    sucesso = False

    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            mensagem = 'As senhas não coincidem.'
        elif User.objects.filter(username=email).exists():
            mensagem = 'Já existe um usuário com esse e-mail.'
        else:
            User.objects.create_user(username=email, email=email, password=password1)
            mensagem = f'Usuário {email} cadastrado com sucesso!'
            sucesso = True

    return render(request, 'monitor/cadastro.html', {
        'mensagem': mensagem,
        'sucesso': sucesso,
    })


@login_required(login_url='/login/')
def gerenciar_incidentes(request):
    if not request.user.is_superuser:
        return redirect('index')

    incidentes = Incidente.objects.filter(resolvido=False).order_by('-data_criacao')
    return render(request, 'monitor/gerenciar_incidentes.html', {'incidentes': incidentes})


@login_required(login_url='/login/')
def editar_incidente(request, incidente_id):
    if not request.user.is_superuser:
        return redirect('index')

    incidente = get_object_or_404(Incidente, id=incidente_id)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        incidente.sistema = request.POST.get('sistema')
        incidente.status = request.POST.get('status')
        incidente.descricao = request.POST.get('descricao')
        incidente.prioridade = request.POST.get('prioridade')

        if acao == 'resolver' or incidente.status == 'Funcionado':
            incidente.resolvido = True

        incidente.save()
        return redirect('gerenciar_incidentes')

    context = {
        'incidente': incidente,
        'sistemas': Incidente.SISTEMA_CHOICES,
        'status_choices': Incidente.STATUS_CHOICES,
        'prioridades': Incidente.PRIORIDADE_CHOICES,
    }
    return render(request, 'monitor/editar_incidente.html', context)
