# How AI Generates Text 3x Faster

## Script

How does AI generate text three times faster without losing quality. Sa ChatGPT, minsan napapansin mong biglang lumilipad ang bilis ng mga salita. Akala ng marami, pinalakas lang ang GPU. Pero may matalinong trick sa likod nito.

Standard AI models are autoregressive. Bago mailabas ang susunod na salita, binabasa ang lahat ng naunang salita. Isa-isang token lang ang kalkulasyon, kaya mabagal kung isa-isa lang lalabas.

Dito nagkakaroon ng bottleneck. Ang isang seventy-billion parameter model ay kailangang mag-load ng bilyon-bilyong numero mula memory bawat salita. Halos idle ang chip kakahintay ng data transfer.

Para lutasin ito, inimbento ang Speculative Decoding. Nagdadagdag sila ng isang maliit at ultra-fast draft model na assistant.

Napakabilis ng draft model. Sa loob ng ilang milliseconds, hinuhulaan agad nito ang susunod na apat hanggang limang salita bago kumilos ang malaking AI.

Dahil designed ang GPUs sa parallel computing, sinusuri ng malaking AI ang limang salita nang sabay-sabay sa iisang pass, kasing bilis ng pag-check sa iisang salita.

Kapag tama ang hula, sabay-sabay itong tinatanggap. Kung may mali, agad itong itatama ng malaking model nang walang bawas sa talino.

Dahil ang malaking AI pa rin ang humahatol, mathematically identical ang sagot. Walang bawas sa quality, pero three times faster ang bilis, umaabot sa eighty tokens per second.

Ang bilis ng modern AI ay dahil sa matalinong algorithms, hindi lang mas malalaking chips. Ikaw, napansin mo ba ang pagbilis ng AI ngayon? I-comment mo sa baba. Follow me for more tech explained. See yah.
