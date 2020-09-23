# Instalación del entorno
## Requisitos del sistema
Mínimo 9GB de RAM (mínimo) para que en Vagrant/VirtualBox se puedan ejecutar las pruebas correctamente. <br/>
#### Instalación VirtualBox
Última versión en su [página de descargas](https://www.virtualbox.org/)<br/>
La guía de instalación está disponible [aquí](https://www.virtualbox.org/manual/ch02.html)<br/>

#### Instalación Vagrant
Última version en su [página de descargas](https://www.vagrantup.com/downloads.html)<br/>

## Instalación
#### Modificación Vagrantfile
1. Modifica el tamaño del disco (si necesario)
```
# Every Vagrant development environment requires a box. You can search for
  # boxes at https://app.vagrantup.com/boxes/search
  config.vm.box = "ubuntu/bionic64"
  config.disksize.size = '50GB'
```
2. Añade una carpeta compartida entre la máquina y local
```
# Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "ruta_carpeta_local", "/home/vagrant/shared", create: true
```
3. Modifica la memoria de la máquina y añade cores (si necesario)
```
# Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
      # Customize the amount of memory on the VM:
      vb.memory = "12288"
      #vb.cpus = "4"
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]	
  end
```
4. Modifica el script de instalación (si necesario)
```
  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision :shell, :path => "bootstrap.sh"
```
5. Añade los puertos que necesites (si necesario)
```
# Map hosts ports 5000,4567,8080,8888,9200,5601 to local port 5000,4567,8080,8888,9200,5601
  config.vm.network :forwarded_port, guest: 5000, host: 5000
  config.vm.network :forwarded_port, guest: 4567, host: 4567
  config.vm.network :forwarded_port, guest: 8080, host: 8080
  config.vm.network :forwarded_port, guest: 8888, host: 8888
  config.vm.network :forwarded_port, guest: 9200, host: 9200
  config.vm.network :forwarded_port, guest: 5601, host: 5601
end
```

### Instalación
Usa `vagrant up` para comenzar la instalación.<br/>
Una vez finalice la instalción, usa `vagrant ssh` para acceder al terminal.
