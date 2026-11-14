---
title: "Tabletas Android sin gestión: F-Droid y Aurora Store para instalar y actualizar aplicaciones"
date: 2026-11-02
weight: 4
secciones: ["herramientas"]
entradilla: "Con tabletas antiguas que ya no tienen mantenimiento, instalar o actualizar aplicaciones se convierte en el problema. Dos herramientas libres permiten hacerlo sin depender de una cuenta de Google."
fuentes:
  - titulo: "F-Droid"
    url: "https://f-droid.org/"
    medio: "F-Droid"
  - titulo: "Aurora Store"
    url: "https://f-droid.org/packages/com.aurora.store/"
    medio: "F-Droid · versión 4.8.4"
  - titulo: "Aurora Store (web oficial)"
    url: "https://auroraoss.com/"
    medio: "Aurora OSS"
  - titulo: "Aurora Store · documentación"
    url: "https://gitlab.com/AuroraOSS/AuroraStore/-/blob/master/README.md"
    medio: "GitLab · README"
conversacion:
  - "https://t.me/edutictac/112513"
  - "https://t.me/edutictac/112514"
---
En el grupo se planteó qué hacer con unas tabletas Android que el centro compró hace años y que la empresa que las gestionaba ya no mantiene. Sin esa gestión, instalar aplicaciones o actualizarlas desde Play Store deja de ser inmediato.

## F-Droid

[F-Droid](https://f-droid.org/) es un repositorio de aplicaciones Android de software libre. Se instala su propio cliente —no hace falta cuenta de Google— y, según su documentación, desde ahí se descargan y actualizan las aplicaciones disponibles. A cambio, solo ofrece software libre: no encontrarás en él las aplicaciones privativas de Play Store.

## Aurora Store

[Aurora Store](https://f-droid.org/packages/com.aurora.store/) es un cliente libre (GPLv3) no oficial de Google Play. Según su documentación, permite buscar, descargar y actualizar aplicaciones de Play, y funciona con o sin los servicios de Google o microG. Se puede usar con una cuenta personal o con una cuenta anónima. Está disponible en F-Droid y en su web oficial.

Tiene límites que conviene conocer antes de instalarlo:

- Depende de los servidores de Google Play y utiliza una API no oficial, así que un cambio por parte de Google puede dejarlo temporalmente inservible.
- F-Droid advierte de que, por defecto, la lista de aplicaciones y los datos del sistema se envían a los servidores de Google Play, lo que puede servir para identificar el dispositivo.
- No descarga ni actualiza aplicaciones de pago y no puede actualizar las que usan Play Asset Delivery.

## Qué elegir

Si lo que se busca es software libre, F-Droid. Si hace falta una aplicación concreta que solo está en Play, Aurora Store con una cuenta anónima evita crear una cuenta de Google. En tabletas que sigan bajo la gestión del centro, conviene consultar antes con el SAI para no romper la configuración existente.
