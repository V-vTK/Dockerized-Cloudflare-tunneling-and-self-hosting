# Dockerized Cloudflare tunneling & Self-Hosting
 A guide on configuring Cloudflare tunnels for exposing assets on your server without portforwarding or router access. This repository also includes a self-made Docker stack to automatically sync your server's IP with Cloudflare's tunnel 
 configuration through their API and a simple example Docker stack for serving a website through an Nginx reverse proxy. This guide also sets up Portainer for remote management of containers.

### Sneak peak at the portainer dashboard and at your future set up!
![NVIDIA_Share_wDS4233PpQ](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/5339f77d-b3db-44df-a41f-49afe40d477a)
![NVIDIA_Share_RTHmQBOUQV](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/27958c71-657b-44c9-901a-59d6a21102d2)


## Requirements
This is *free* but requires a few things:

Domain name (costs money about 10€/yr)

Computer (preferably a separate one but for trying out this will work on your main computer - skip the SSH setup)

Cloudflare account


## OS
Start with your chosen OS – RHEL, Ubuntu Server, or, for trying out Ubuntu Desktop or Windows. This guide will use a separate computer, referred to as the server, (Intel NUC) with Ubuntu Desktop for easier demonstration. It will be accessed from my main computer, referred to as the client, through SSH. For a permanent home lab, a server OS is recommended.


## SSH
If you don't have the software for a SSH server:
```sudo apt update```
```sudo apt install openssh-server```
```sudo systemctl restart ssh```
```sudo ufw allow OpenSSH```
This is the bare minimum set up ssh keys and other settings

You can find out the IP via ```ping <hostname>``` or on the server ```ip a```
e.g. ```ping vv-NUC```

Then we can connect to the server with the client machine:
```ssh username@ipv4address``` e.g. ssh ```vv@192.168.1.1```

FTP clients like FileZilla can be used to easily transfer files to the server. It uses the same credentials as the SSH.
https://filezilla-project.org/

## Docker
Download Docker:
https://docs.docker.com/engine/install/ubuntu/

And for those who want it Docker Desktop for Ubuntu Desktop:

https://docs.docker.com/desktop/install/linux-install/

Set up docker-compose to use version 2 - Stacks show up in Portainer

![image](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/a52f67da-d7c5-4e85-a401-584b750f35b6)

## Cloudflare Tunnels

Make a Cloudflare account

Get your domain through Cloudflare or transfer domain name servers to them:

https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/

### Cloudflare:

Home/ZeroTrust

Set up a team name

Home/ZeroTrust/Access/Tunnels

Set up a payment method (It is free but the payment method is an additional verification)

### Create a new Tunnel

Choose your environment docker

Copy the command ```docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token ...```

Add a few flags to it

```--name cloudflare_tunnel // name```

```--restart=unless-stopped // restart flag```

```-d //run seperately in the background```

Command should look like this:

```docker run --name cloudflare_tunnel --restart=unless=stopped -d cloudflare/cloudflared:latest tunnel --no-autoupdate run --token ...```

After running the command the Tunnel status should turn to healthy in the Cloudflare access/tunnels dashboard.

The terminal can be seen with:
```docker ps```
And shut down with
```docker stop cloudflare_tunnel```

## Portainer
Portainer is a dashboard for maintaining your docker containers

Run ```docker volume create portainer_data``` to create a docker volume for portainer this is for persistent data 

Run ```docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest``` to create the Portainer container

now you can head over to localhost:9443

![image](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/27e7a07f-b71b-4b60-a2cd-19208cadd7a6)

Set up your username and password

## Website demo
A simple Vite React project served with Nginx to showcase a reverse proxy. A backend is very easy to add to the nginx.conf.
Download the NginxProxyServe folder and open a terminal at that folder
Run ```docker compose up -d```
Head over to localhost:4343 to see the website

## Expose to the internet

Setup a few public hostnames for the website and for portainer
Home/ZeroTrust/Access/Tunnels/yourTunnel/Public Hostname
Add a public hostname:

![image](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/74241c70-c10c-4e5e-92c6-0311f0dd73d0)


and for Portainer set No TLS Verify from Additional application settings (This setting is only needed for Portainer) 

![chrome_tw2OJCml7m](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/8977cd5d-78dd-4aff-b6f3-59c1c599403c)


Same for your website except change the subdomain to your liking and change the port (":9443" for portainer) to 4343


The websites should be viewable at their addresses - portainer.yourdomain.com


## Securing Portainer
In addition to your password we can add an additional layer of security with cloudflare


Head to Home/ZeroTrust/Access/Applications

Add an application: selfhosted

![NVIDIA_Share_TDpEyLXavv](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/65fd8e29-9bac-4ebe-a504-329b185dab23)

![NVIDIA_Share_SFJLCePq0Y](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/52651c9f-3184-44d3-857c-4a8e3b964a08)

![NVIDIA_Share_TRYvQQjFWe](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/2137a070-779e-4bad-b001-c8d10e2f0163)


Now when going to portainer.yourdomain.com Cloudflare will ask for a code sent to your email before transfering you to the portainer login screen (read as 2FA).

![NVIDIA_Share_Xfas8wNR6c](https://github.com/V-vTK/Dockerized-Cloudflare-tunneling-and-self-hosting/assets/97534406/b6fe58c4-6ad9-43ef-9fd5-1a92dab4213e)



## IP_manager
If obtaining a static IP proves challenging using DHCP reservations or the standard static IP configuration (read as no router access). I have created a docker stack to update the cloudflare tunnel service IP's automatically.

Download the IP-manager

Change the .envexample to .env and insert your credentials: api_token (not api_key), zone_id, account_id, tunnel_id, and domain.

run ```docker compose up -d``` inside the folder

Now the IP_manager container will check your IP every 5 minutes and update the IP inside the Cloudflare public hostnames if the IP has changed.
Works using the Cloudflare API v4: https://cfapi.centminmod.com/#cloudflare-tunnel-configuration-put-configuration




