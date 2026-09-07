# ==============================================================================
# Receta principal de Chef — Configuración del servidor de agentes
# Proyecto: Sistema Multiagentes - Turismo Médico Sonora (Equipo Charlie)
# ==============================================================================
# Esta receta se ejecuta DENTRO de la máquina EC2 que crea Terraform.
# Instala y configura todo lo necesario para que los agentes funcionen.
# ==============================================================================

# 1. Actualizar repositorios del sistema
execute 'apt_update' do
  command 'apt-get update -y'
  action :run
end

# 2. Instalar Python 3 y herramientas básicas
%w[python3 python3-pip python3-venv git curl wget awscli].each do |pkg|
  package pkg do
    action :install
  end
end

# 3. Instalar librerías del sistema para Playwright / Chromium headless
%w[
  libnss3
  libatk1.0-0
  libatk-bridge2.0-0
  libcups2
  libdrm2
  libxcomposite1
  libxdamage1
  libxrandr2
  libgbm1
  libpango-1.0-0
  libcairo2
  libasound2
  libxshmfence1
].each do |pkg|
  package pkg do
    action :install
  end
end

# 4. Crear carpeta de trabajo para los agentes
directory '/opt/multiagent-system' do
  owner 'ubuntu'
  group 'ubuntu'
  mode '0755'
  recursive true
  action :create
end

directory '/opt/multiagent-system/data' do
  owner 'ubuntu'
  group 'ubuntu'
  mode '0755'
  action :create
end

# 5. Instalar dependencias Python globales para el agente de scraping
execute 'instalar_paquetes_python' do
  command 'pip3 install beautifulsoup4 playwright'
  action :run
end

execute 'instalar_chromium_playwright' do
  command 'playwright install --with-deps chromium'
  environment 'HOME' => '/root'
  action :run
end

# 6. Cron Job para ejecutar el scraper automáticamente a las 6:00 AM UTC
cron 'ejecutar_scraper_diario' do
  minute '0'
  hour '6'
  user 'ubuntu'
  command 'cd /opt/multiagent-system && python3 Scrapper_info.py >> /var/log/scraper.log 2>&1'
  action :create
end
