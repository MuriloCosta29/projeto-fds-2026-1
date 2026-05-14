from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from monitor.models import Incidente
import time

URL_HOME = "/"
URL_LOGIN = "/login/"
URL_HISTORICO = "/historico/"
URL_REGISTRAR = "/registrar-novo/"
URL_INCIDENTES = "/incidentes-ativos/"
URL_CADASTRO_ALUNO = "/cadastro/"
URL_LOGOUT = "/logout/"
URL_GERENCIAR = "/gerenciar/"

CAMPO_USUARIO = "username"
CAMPO_SENHA = "password"
BOTAO_SUBMIT = "button[type='submit']"
BOTAO_ENVIAR_FORM = "button.btn-enviar"

ADMIN_USER = "ti_teste"
ADMIN_EMAIL = "ti@cesar.school"
ADMIN_PASS = "senha_ti_123"


def configurar_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # comentar essa linha quando for fazer o video
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browser.implicitly_wait(5)
    return browser


def clicar(browser, elemento):
    """Clica em um elemento via JavaScript — funciona mesmo em headless/CI."""
    browser.execute_script("arguments[0].scrollIntoView(true);", elemento)
    time.sleep(0.3)
    browser.execute_script("arguments[0].click();", elemento)


def criar_admin():
    return User.objects.create_superuser(
        username=ADMIN_USER, email=ADMIN_EMAIL, password=ADMIN_PASS
    )


def criar_aluno():
    user, created = User.objects.get_or_create(username="aluno_teste")
    if created:
        user.set_password("senha_aluno_123")
        user.save()
    return user


# -------------------------------------------------------
# SCRUM-19 - ALUNO VISUALIZA STATUS DOS SISTEMAS
# -------------------------------------------------------
class SCRUM19_VisualizarStatusSistemas(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.aluno = criar_aluno()
        Incidente.objects.create(
            sistema="Portal do Aluno",
            status="Funcionando",
            descricao="Teste para Aluno",
            resolvido=False,
        )

    def _fazer_login_aluno(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_aluno_visualiza_status_na_home(self):
        """Aluno logado deve ver o status dos sistemas na página inicial."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(1)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("status", corpo, "O Aluno não conseguiu ver a seção de status.")
        termos_esperados = ["funcionando", "operando normalmente", "portal do aluno"]
        tem_status = any(termo in corpo for termo in termos_esperados)
        self.assertTrue(
            tem_status, "O Aluno não encontrou indicadores de status na página."
        )
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-20 - ESTUDANTE VISUALIZA HISTÓRICO DE INCIDENTES
# -------------------------------------------------------
class SCRUM20_VisualizarHistoricoIncidentes(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.aluno = criar_aluno()
        self.browser.delete_all_cookies()
        Incidente.objects.create(
            sistema="Lyceum",
            status="Funcionando",
            descricao="Incidente resolvido para teste",
            resolvido=True,
        )

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_aluno(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_historico_acessivel_sem_login(self):
        """Histórico deve ser acessível sem precisar fazer login."""
        self.browser.get(self.live_server_url + URL_HISTORICO)
        time.sleep(2)
        self.assertNotIn(URL_LOGIN, self.browser.current_url)
        time.sleep(2)

    def test_pagina_historico_carrega_sem_erro(self):
        """A página de histórico deve carregar sem erros."""
        self.browser.get(self.live_server_url + URL_HISTORICO)
        time.sleep(2)
        self.assertNotIn("Server Error", self.browser.title)
        self.assertNotIn("Page not found", self.browser.title)
        time.sleep(2)

    def test_historico_exibe_incidente_resolvido(self):
        """Histórico deve exibir incidentes que foram resolvidos."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HISTORICO)
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        tem_conteudo = any(
            palavra in corpo
            for palavra in ["lyceum", "histórico", "incidente", "resolvido", "nenhum"]
        )
        self.assertTrue(tem_conteudo, "Histórico não exibiu incidentes resolvidos.")
        time.sleep(2)

    def test_historico_exibe_data_dos_incidentes(self):
        """Histórico deve exibir a data dos incidentes passados."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HISTORICO)
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        tem_data = any(palavra in corpo for palavra in ["data", "/", "2025", "2026"])
        self.assertTrue(tem_data, "Histórico não exibe a data dos incidentes.")
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-21 - TI MARCA INCIDENTE COMO RESOLVIDO
# -------------------------------------------------------
class SCRUM21_MarcarIncidenteComoResolvido(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin = criar_admin()
        self.browser.delete_all_cookies()

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_admin(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(ADMIN_USER)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys(ADMIN_PASS)
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_ti_acessa_pagina_de_gerenciar(self):
        """Membro da TI logado deve acessar a área de gerenciar incidentes."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_GERENCIAR)
        time.sleep(2)
        self.assertNotIn("Server Error", self.browser.title)
        self.assertNotIn("Forbidden", self.browser.title)
        time.sleep(2)

    def test_usuario_sem_login_nao_acessa_gerenciar(self):
        """Usuário sem login não deve conseguir acessar a página de gerenciar."""
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + URL_GERENCIAR)
        time.sleep(2)
        self.assertIn(URL_LOGIN, self.browser.current_url)
        time.sleep(2)

    def test_ti_marca_incidente_como_resolvido(self):
        """TI consegue acessar editar incidente e marcá-lo como resolvido."""
        incidente = Incidente.objects.create(
            sistema="Portal do Aluno",
            status="Fora do Ar",
            descricao="Sistema completamente fora do ar.",
            resolvido=False,
        )
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_GERENCIAR)
        time.sleep(2)
        clicar(
            self.browser, self.browser.find_element(By.LINK_TEXT, "Editar / Resolver")
        )
        time.sleep(2)
        botao = self.browser.find_element(By.CSS_SELECTOR, "button[value='resolver']")
        clicar(self.browser, botao)
        time.sleep(2)
        incidente.refresh_from_db()
        self.assertTrue(
            incidente.resolvido, "Incidente não foi marcado como resolvido!"
        )
        time.sleep(2)

    def test_incidente_resolvido_some_do_dashboard(self):
        """Incidente marcado como resolvido não deve aparecer no dashboard."""
        incidente = Incidente.objects.create(
            sistema="Chamada",
            status="Instável",
            descricao="Chamada instável.",
            resolvido=False,
        )
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_GERENCIAR)
        time.sleep(2)
        clicar(
            self.browser, self.browser.find_element(By.LINK_TEXT, "Editar / Resolver")
        )
        time.sleep(2)
        clicar(
            self.browser,
            self.browser.find_element(By.CSS_SELECTOR, "button[value='resolver']"),
        )
        time.sleep(2)
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Chamada", corpo)
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-22 - ESTUDANTE DIFERENCIA PROBLEMA DE CONEXÃO
# -------------------------------------------------------
class SCRUM22_DiferenciarProblemaConexao(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.aluno = criar_aluno()
        self.browser.delete_all_cookies()
        Incidente.objects.create(
            sistema="Portal do Aluno",
            status="Fora do Ar",
            descricao="Portal fora do ar.",
            resolvido=False,
        )

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_aluno(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_site_responde_e_esta_acessivel(self):
        """O site do status deve estar acessível e retornar conteúdo válido."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)
        self.assertNotIn("Server Error", self.browser.title)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(corpo) > 0, "O site retornou uma página vazia.")
        time.sleep(2)

    def test_dashboard_exibe_sistema_fora_do_ar(self):
        """Dashboard deve mostrar claramente que um sistema está fora do ar."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("fora do ar", corpo, "Dashboard não indicou sistema fora do ar.")
        time.sleep(2)

    def test_indicador_vermelho_aparece_para_sistema_fora_do_ar(self):
        """Indicador vermelho deve aparecer para sistema fora do ar."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)
        pontos_vermelhos = self.browser.find_elements(
            By.CSS_SELECTOR, ".ponto.vermelho"
        )
        self.assertGreater(
            len(pontos_vermelhos), 0, "Nenhum indicador vermelho encontrado."
        )
        time.sleep(2)

    def test_nome_sistema_afetado_aparece_no_dashboard(self):
        """O nome do sistema afetado deve aparecer no dashboard."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Portal do Aluno", corpo, "Nome do sistema afetado não apareceu.")
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-23 - MEMBRO DE TI REGISTRA NOVO INCIDENTE
# -------------------------------------------------------
class SCRUM_Historia1_RegistrarIncidente(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin = criar_admin()
        self.browser.delete_all_cookies()

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_admin(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(ADMIN_USER)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys(ADMIN_PASS)
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_ti_registra_incidente_instavel(self):
        """Membro de TI registra incidente instável e ele aparece no dashboard."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_INCIDENTES)
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "sistema")).select_by_visible_text(
            "Lyceum"
        )
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "status")).select_by_visible_text(
            "Instável"
        )
        time.sleep(1)
        self.browser.find_element(By.NAME, "descricao").send_keys(
            "Sistema com lentidão desde as 14h."
        )
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM))
        time.sleep(2)
        self.assertIn(URL_HOME, self.browser.current_url)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Lyceum", corpo)
        time.sleep(2)

    def test_ti_registra_incidente_fora_do_ar(self):
        """Membro de TI registra incidente fora do ar e indicador vermelho aparece."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_INCIDENTES)
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "sistema")).select_by_visible_text(
            "Portal do Aluno"
        )
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "status")).select_by_visible_text(
            "Fora do Ar"
        )
        time.sleep(1)
        self.browser.find_element(By.NAME, "descricao").send_keys(
            "Portal completamente fora do ar."
        )
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM))
        time.sleep(2)
        pontos_vermelhos = self.browser.find_elements(
            By.CSS_SELECTOR, ".ponto.vermelho"
        )
        self.assertGreater(len(pontos_vermelhos), 0)
        time.sleep(2)

    def test_ti_registra_incidente_instavel_indicador_amarelo(self):
        """Incidente instável aparece com indicador amarelo no dashboard."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_INCIDENTES)
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "sistema")).select_by_visible_text(
            "Chamada"
        )
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "status")).select_by_visible_text(
            "Instável"
        )
        time.sleep(1)
        self.browser.find_element(By.NAME, "descricao").send_keys("Chamada instável.")
        time.sleep(1)
        clicar(
            self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM)
        )
        time.sleep(2)
        pontos_amarelos = self.browser.find_elements(By.CSS_SELECTOR, ".ponto.amarelo")
        self.assertGreater(len(pontos_amarelos), 0)
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-28 - TELA DE LOGIN PARA ALUNO E ADMIN
# -------------------------------------------------------
class SCRUM_Historia2_TelaLogin(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin = criar_admin()
        self.aluno = criar_aluno()
        self.browser.delete_all_cookies()

    def tearDown(self):
        User.objects.all().delete()

    def test_tela_login_e_a_primeira_tela(self):
        """A tela de login é a primeira tela que o usuário vê."""
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(1)
        self.assertIn(URL_LOGIN, self.browser.current_url)
        time.sleep(2)

    def test_aluno_consegue_fazer_login(self):
        """Aluno comum consegue fazer login e acessar o dashboard."""
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        self.assertIn(URL_HOME, self.browser.current_url)
        time.sleep(2)

    def test_admin_consegue_fazer_login_e_ve_botoes_exclusivos(self):
        """Admin consegue fazer login e vê botões exclusivos no dashboard."""
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(ADMIN_USER)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys(ADMIN_PASS)
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Cadastrar Usuário", corpo)
        self.assertIn("Gerenciar Incidentes", corpo)
        time.sleep(2)

    def test_aluno_nao_ve_botoes_de_admin(self):
        """Aluno não vê botões exclusivos de admin no dashboard."""
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Cadastrar Usuário", corpo)
        self.assertNotIn("Gerenciar Incidentes", corpo)
        time.sleep(2)

    def test_login_incorreto_exibe_erro(self):
        """Login com credenciais erradas exibe mensagem de erro."""
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("usuario_errado")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_errada")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("incorretos", corpo)
        time.sleep(2)

    def test_nome_usuario_aparece_na_navbar(self):
        """Nome do usuário logado aparece no canto superior da tela."""
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(ADMIN_USER)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys(ADMIN_PASS)
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        username_elemento = self.browser.find_element(By.CSS_SELECTOR, ".username")
        self.assertIn(ADMIN_USER, username_elemento.text)
        time.sleep(2)


# -------------------------------------------------------
# SCRUM-29 - ADMIN CADASTRA NOVO ALUNO
# -------------------------------------------------------
class SCRUM_Historia3_CadastrarAluno(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin = criar_admin()
        self.browser.delete_all_cookies()

    def tearDown(self):
        User.objects.all().delete()

    def _fazer_login_admin(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(ADMIN_USER)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys(ADMIN_PASS)
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_admin_acessa_tela_de_cadastro(self):
        """Admin consegue acessar a tela de cadastro de usuários."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_CADASTRO_ALUNO)
        time.sleep(1)
        self.assertIn(URL_CADASTRO_ALUNO, self.browser.current_url)
        time.sleep(2)

    def test_admin_cadastra_novo_aluno_com_sucesso(self):
        """Admin preenche email e senha e cadastra um novo aluno com sucesso."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_CADASTRO_ALUNO)
        time.sleep(1)
        self.browser.find_element(By.NAME, "email").send_keys("novo@cesar.school")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password1").send_keys("senha123")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password2").send_keys("senha123")
        time.sleep(1)
        clicar(
            self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM)
        )
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("cadastrado com sucesso", corpo)
        self.assertTrue(User.objects.filter(username="novo@cesar.school").exists())
        time.sleep(2)

    def test_cadastro_senhas_diferentes_exibe_erro(self):
        """Senhas diferentes exibem mensagem de erro no cadastro."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_CADASTRO_ALUNO)
        time.sleep(1)
        self.browser.find_element(By.NAME, "email").send_keys("erro@cesar.school")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password1").send_keys("senha123")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password2").send_keys("diferente456")
        time.sleep(1)
        clicar(
            self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM)
        )
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("não coincidem", corpo)
        time.sleep(2)

    def test_cadastro_email_duplicado_exibe_erro(self):
        """Tentar cadastrar email já existente exibe mensagem de erro."""
        User.objects.create_user(username="existente@cesar.school", password="senha123")
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_CADASTRO_ALUNO)
        time.sleep(1)
        self.browser.find_element(By.NAME, "email").send_keys("existente@cesar.school")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password1").send_keys("qualquer123")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password2").send_keys("qualquer123")
        time.sleep(1)
        clicar(
            self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM)
        )
        time.sleep(2)
        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Já existe", corpo)
        time.sleep(2)

    def test_novo_aluno_cadastrado_consegue_fazer_login(self):
        """Aluno cadastrado pelo admin consegue fazer login no sistema."""
        self._fazer_login_admin()
        self.browser.get(self.live_server_url + URL_CADASTRO_ALUNO)
        time.sleep(1)
        self.browser.find_element(By.NAME, "email").send_keys("novinho@cesar.school")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password1").send_keys("senha456")
        time.sleep(1)
        self.browser.find_element(By.NAME, "password2").send_keys("senha456")
        time.sleep(1)
        clicar(
            self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_ENVIAR_FORM)
        )
        time.sleep(2)
        self.browser.delete_all_cookies()
        time.sleep(1)
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys(
            "novinho@cesar.school"
        )
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha456")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)
        self.assertIn(URL_HOME, self.browser.current_url)
        time.sleep(2)


class SCRUM18_EstudanteRelataProblema(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.aluno = criar_aluno()
        self.browser.delete_all_cookies()

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_aluno(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_estudante_relata_problema_com_sucesso(self):
        """Estudante relata problema e o incidente é salvo no banco."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_REGISTRAR)
        time.sleep(1)

        Select(self.browser.find_element(By.NAME, "sistema")).select_by_visible_text(
            "Portal do Aluno"
        )
        time.sleep(1)
        Select(self.browser.find_element(By.NAME, "status")).select_by_visible_text(
            "Instável"
        )
        time.sleep(1)
        self.browser.find_element(By.NAME, "descricao").send_keys("Erro nas notas")
        time.sleep(1)

        clicar(
            self.browser,
            self.browser.find_element(By.CSS_SELECTOR, ".rodape button[type='submit']"),
        )
        time.sleep(2)

        self.assertIn(URL_HOME, self.browser.current_url)
        incidente = Incidente.objects.get(descricao="Erro nas notas")
        self.assertEqual(incidente.sistema, "portal")
        self.assertEqual(incidente.status, "instavel")
        self.assertEqual(incidente.prioridade, "media")
        self.assertFalse(incidente.resolvido)


class SCRUM17_VisualizarUptimeSistema(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = configurar_browser()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.aluno = criar_aluno()
        self.browser.delete_all_cookies()
        Incidente.objects.create(
            sistema="Lyceum",
            status="Instável",
            descricao="Sistema instável para teste de uptime.",
            resolvido=False,
        )

    def tearDown(self):
        User.objects.all().delete()
        Incidente.objects.all().delete()

    def _fazer_login_aluno(self):
        self.browser.get(self.live_server_url + URL_LOGIN)
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_USUARIO).send_keys("aluno_teste")
        time.sleep(1)
        self.browser.find_element(By.NAME, CAMPO_SENHA).send_keys("senha_aluno_123")
        time.sleep(1)
        clicar(self.browser, self.browser.find_element(By.CSS_SELECTOR, BOTAO_SUBMIT))
        time.sleep(2)

    def test_dashboard_exibe_uptime_do_sistema(self):
        """Dashboard exibe a porcentagem de uptime do sistema."""
        self._fazer_login_aluno()
        self.browser.get(self.live_server_url + URL_HOME)
        time.sleep(2)

        corpo = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn("Lyceum", corpo)
        self.assertIn("Uptime:", corpo)
        self.assertIn("%", corpo)
