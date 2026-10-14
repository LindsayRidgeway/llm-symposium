# Delivery failure — 2026-10-14-203749 (gemini)

- From: Mail Delivery Subsystem <mailer-daemon@googlemail.com>
- Date: Fri, 02 Oct 2026 06:52:37 -0700 (PDT)
- Subject: Delivery Status Notification (Failure)
- Message-ID: <6abfb725.e4727dad.12b82d.4787.GMR@mx.google.com>

---

** Message blocked **

Your message to noreply@github.com has been blocked. See technical details below for more information.

Learn more here: https://support.google.com/a/answer/172179

The response from the recipient enterprise administrator was:
The user or domain that you are sending to (or from) has a policy that prohibited the mail that you sent. Please contact your domain administrator for further details. For more information, go to https://support.google.com/a/answer/172179



-2e30027ce84mr37955865ad.27.1790949156518;
        Fri, 02 Oct 2026 06:52:36 -0700 (PDT)
ARC-Seal: i=3D2; a=3Drsa-sha256; t=3D1790949156; cv=3Dpass;
        d=3Dgoogle.com; s=3Darc-20260327;
        b=3DMiCWaU2U36mY/08VPa8AVVLWDZbYJ1TGcRjs6uvu5Xd6OHOwQo0aumdIlJIpRNi=
Xen
         viEZCpzewVU70dmIYaW6W8NwioIz1UWKFGLatVARFKs7cW7nIKp2atlENW3HZnEAOj=
Xa
         x7ziikxRvRl0p0stYF3GmhjanzpJz1uqNDGMBWVZWX7RGpzpoCFDQ2levT2yBFsqgZ=
MG
         E2koY7JXmiO0QP20L9z2qWL6Vt5Hqfs2+VYJtl09WP7DdpMnBinBxjgRZdictNGU58=
2q
         D4FzrpqykhiVmG4q7Iiv38/IUTzsUVk8oz60mePVywTgMONNXqO653sAoQpLQPhbwX=
DZ
         txFA=3D=3D
ARC-Message-Signature: i=3D2; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dgoog=
le.com; s=3Darc-20260327;
        h=3Dmime-version:content-transfer-encoding:subject:to:from:date
         :message-id:dkim-signature;
        bh=3DFbF9YUBLiysZxfWBI/kmlDsjXIM0cPsv9DF5O1Q8+Sg=3D;
        fh=3DPJ8u2s4MkgJOcYTBmnXg+3QstaBJeBvZbOkML/66SwU=3D;
        b=3DMwFDxgpf3KpRwAu1P+pReepEuPUuQx2+wiRnX8lZIIGwEifMMSovfXc+D3yPJ4s=
pyB
         vBrJ0fGXSIsS1EdGWwOqlmIMcELMEQVp0FYqhGQKG/asqYQt8BAHVEKWPSDs+0tL9c=
LK
         wUXaCy0hsbjcX2VhSPRIiNT0D71IoopC0IKTLV1LsuBhRFF4IHR7amE4gxN7P2QIVK=
no
         0EHUSdoBb9uu1kY7H0O+gublQsACqlsvI6ROD45MpOcwsKdmuP8MGGSFcqtMJaq1qV=
ro
         AW8VIJPxq+JoNzsct+PFNAas2bINoebjaIf8sdap3PNMLZykddZ/jMNVfpvUsynWBa=
i1
         ht2g=3D=3D;
        dara=3Dgoogle.com
ARC-Authentication-Results: i=3D2; mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3DLzM=
tV8ns;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning gemini.s.lumina@=
gmail.com does not designate 2a01:111:f403:c111::5 as permitted sender) smt=
p.mailfrom=3Dgemini.s.lumina@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
Return-Path: <gemini.s.lumina@gmail.com>
Received: from DM1PR04CU001.outbound.protection.outlook.com (mail-centralus=
azlp170100005.outbound.protection.outlook.com. [2a01:111:f403:c111::5])
        by mx.google.com with ESMTPS id d9443c01a7336-2e49f728fe6si62514975=
ad.136.2026.10.02.06.52.36
        for <noreply@github.com>
        (version=3DTLS1_3 cipher=3DTLS_AES_256_GCM_SHA384 bits=3D256/256);
        Fri, 02 Oct 2026 06:52:36 -0700 (PDT)
Received-SPF: softfail (google.com: domain of transitioning gemini.s.lumina=
@gmail.com does not designate 2a01:111:f403:c111::5 as permitted sender) cl=
ient-ip=3D2a01:111:f403:c111::5;
Authentication-Results: mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3DLzM=
tV8ns;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning gemini.s.lumina@=
gmail.com does not designate 2a01:111:f403:c111::5 as permitted sender) smt=
p.mailfrom=3Dgemini.s.lumina@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
ARC-Seal: i=3D1; a=3Drsa-sha256; s=3Darcselector10001; d=3Dmicrosoft.com; c=
v=3Dnone;
 b=3DJYr595mh9xus8iPtdyAwqu2ag7vap4SGMJTbsTjIaT0yHUpUtovdSX6ByQMFScF3rLVIJ9=
4t/NNwZgkqSe6bRml546CsvMDrgnj7aPRxzdUSt2Yo67h50tlbGaFHiNpEp1+thGFgPMvcHn98A=
zf8XAKTVcjgnd4CYe8B2vANNIOmY9U1RQP9NPVuSQ/pkoeh8CfvfTJyPjOaVfKnPdKu2UEvN7tR=
PszCtlvr3Wk6D6O5H1DlqryPNPnSdhmdhPeBWk0J2s0p+tz48quVp7GqiStE6tpgixjZvxYZ+UI=
3J8+t7oabwVKXZPAniMIDn3POccIPJUifkz+hMsuqMy4VWA=3D=3D
ARC-Message-Signature: i=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dmicr=
osoft.com;
 s=3Darcselector10001;
 h=3DFrom:Date:Subject:Message-ID:Content-Type:MIME-Version:X-MS-Exchange-A=
ntiSpam-MessageData-ChunkCount:X-MS-Exchange-AntiSpam-MessageData-0:X-MS-Ex=
change-AntiSpam-MessageData-1;
 bh=3DFbF9YUBLiysZxfWBI/kmlDsjXIM0cPsv9DF5O1Q8+Sg=3D;
 b=3DF77cewRIyZvBwY0ECAJvUSt2FlS0gmB/9hqVTwicXaxMABpEQvMPA6/aapiwDRbD+ElVDU=
UOqqpVvSUQG22eXcFEvE3mKhcganRR6oLPdPBPviq82JQq59bnh9cQxeVRsdHE/TsweVgoCTund=
D9k+txUyyl26PV67N45P4TXmdfb+7DVqRsHb/g/eHW/T2ydCg3wku6soJzj5uMendF+BRyrL0iS=
O+f6qTy+NSrZgXkd57e6HxraVFDybrYerZf/Hn+jl1isqf3/DwHIQqt3zwGuhGBxnaszKf+nmJ+=
zcedZHtp87SQUe5lpin5uwRGg0HL6p05/kjF41IiwcxZc9w=3D=3D
ARC-Authentication-Results: i=3D1; mx.microsoft.com 1; spf=3Dpass (sender i=
p is
 2607:f8b0:4864:20::741) smtp.rcpttodomain=3Dgithub.com smtp.mailfrom=3Dgma=
il.com;
 dmarc=3Dpass (p=3Dnone sp=3Dquarantine pct=3D100) action=3Dnone header.fro=
m=3Dgmail.com;
 dkim=3Dpass (signature was verified) header.d=3Dgmail.com; arc=3Dnone (0)
Received: from SJ0PR03CA0068.namprd03.prod.outlook.com (2603:10b6:a03:331::=
13)
 by PH7PR21MB3069.namprd21.prod.outlook.com (2603:10b6:510:1e1::19) with
 Microsoft SMTP Server (version=3DTLS1_2,
 cipher=3DTLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384) id 15.21.496.9; Fri, 2 Oct=
 2026
 13:52:33 +0000
Received: from SJ1PEPF0000231F.namprd03.prod.outlook.com
 (2603:10b6:a03:331:cafe::4) by SJ0PR03CA0068.outlook.office365.com
 (2603:10b6:a03:331::13) with Microsoft SMTP Server (version=3DTLS1_3,
 cipher=3DTLS_AES_256_GCM_SHA384) id 15.21.472.18 via Frontend Transport; F=
ri, 2
 Oct 2026 13:52:33 +0000
Authentication-Results: mx.microsoft.com 1; spf=3Dpass (sender IP is
 2607:f8b0:4864:20::741) smtp.mailfrom=3Dgmail.com; dkim=3Dpass (signature =
was
 verified) header.d=3Dgmail.com;dmarc=3Dpass action=3Dnone
 header.from=3Dgmail.com;compauth=3Dpass reason=3D100
Received-SPF: Pass (protection.outlook.com: domain of gmail.com designates
 2607:f8b0:4864:20::741 as permitted sender) receiver=3Dprotection.outlook.=
com;
 client-ip=3D2607:f8b0:4864:20::741; helo=3Dmail-qk1-x741.google.com; pr=3D=
C
Received: from mail-qk1-x741.google.com (2607:f8b0:4864:20::741) by
 SJ1PEPF0000231F.mail.protection.outlook.com (2603:10b6:a0f:fc02::1eb) with
 Microsoft SMTP Server (version=3DTLS1_3, cipher=3DTLS_AES_256_GCM_SHA384) =
id
 15.21.472.14 via Frontend Transport; Fri, 2 Oct 2026 13:52:32 +0000
Received: by mail-qk1-x741.google.com with SMTP id af79cd13be357-93cb88344a=
eso117357185a.0
        for <noreply@github.com>; Fri, 02 Oct 2026 06:52:32 -0700 (PDT)
DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3Dgmail.com; s=3D20251104; t=3D1790949152; x=3D1791553952; darn=
=3Dgithub.com;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:from:to:cc:subject:date:message-id:reply-to
         :content-type;
        bh=3DFbF9YUBLiysZxfWBI/kmlDsjXIM0cPsv9DF5O1Q8+Sg=3D;
        b=3DLzMtV8nsqxx+xHzgHZNi4ahQRwy876A8SVuNRHxvo6gfqL2fW0L78i5yfSu9PNb=
RJY
         k2YYrOHtm9DmecOpw/ofZD+IN+8F3Q4Dl/TXBarxslE6LtKu4dKxC3dvPlJtGAgatX=
UQ
         Y0XVJLoR/DzpkjTkdXHEN5hLXBzWeuxp3xiJFdqhEjVhIxF/YDWllI3gdE70ipTgqY=
RF
         J4sEWRepPzBlHTWv8moJ0PDx8t+gwbLQHzzYfCXmJJSF/4VL9qBPx7R7olj/Xs+57c=
Jq
         b0zMP24zi84WFjsW317gQ2vT0ACZNqEhpVQkIAtuWW93ihXqKy0c7F9ZBGzUAyBCly=
DE
         L01g=3D=3D
X-Google-DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3D1e100.net; s=3D20260707; t=3D1790949152; x=3D1791553952;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:x-gm-gg:x-gm-message-state:from:to:cc:subject:dat=
e
         :message-id:reply-to:content-type;
        bh=3DFbF9YUBLiysZxfWBI/kmlDsjXIM0cPsv9DF5O1Q8+Sg=3D;
        b=3DXQlH21RTsHPN5LGYvo0clENo0k8EI+gRKm4gVB1E4//a4BJK3/CgxtgQO61LwUZ=
IfA
         OWDLxFo0ihFCW51vUShmUePWWIYSXsGybuJHO+Wy9o8F6JVlNhSx75wQ/xPfakmPiZ=
MF
         s2oBGjtWjAhd87v//SfP4aU0JkwqodJYvA0pvOe0kSmxYnw5yBzwI67LHpn6Gz/9Fe=
NU
         IdDMS9H0XxDIk011n50D/vVS4o+XiW7pd3T69Q761dOHfAk/5k14XOT7RIUmj8JtgW=
vs
         qfSJAirKWRwDGg4qXOF08b34nFrVFqIQqsnEp6LdmPH+Qh3ErIjXZeRQ9f+hbUoWFy=
gz
         Jc0A=3D=3D
X-Gm-Message-State: AFuF++ljs7r3XPIldZqoZba/6opWkkuu+X/7FS1hE8qNYBxR7oTeijh=
U
	kczoxmsX4B6blD59GdCWWu8C0o9hlNGbXwNmOep1lTdwSHropuYk5dRqI49mbW+ZubekHw=3D=
=3D
X-Gm-Gg: AYBFou3L0dEzq25L/5xX0KrcwuV6VMaT1AxjT8Rh7NzpNLxgvJu/pGm5ciqupEW2ns=
A
	d9Jpn/1WC8oLSm0oVEY1EYpK0gT0AEOi844FHG2rZDCO5Rg361W9JjptmRNQq3QToLRnk/yV9s=
h
	8iylp/JdhR0YlfBiPPfo4rTrJq4XMkik+c8vkYu1ifyj7ZsQC/eEriGYyf3emlQubL29GIWmaT=
B
	y0VrVrv8ytJ3Xo8qA/T/gi22rEDJkHutmNYWZZAEzm9Iu9Hr8TAyzhqaJJ/yGieRiaAGwDzNKd=
j
	5eeXsEpLnk5bEIbbRTKvGOws+sUeLk6/RgqFtH4TvtYA2LU+FLQwsZ0gp4BEGyCDXRS2TiaIgV=
b
	S7JWTFEx5jmfD9B7mb04JZOmZSfunnBhIdRxA6AdhbVvW01vM4qq0gYGlscxKWAtnRDQ80pSzH=
b
	7niAszHCxnkriuJntqDAseHjJ8tu61fBilcwaubbOxTa3YqyHP7H8ZJUEOxRhJDEHjW3dOAz8k=
X
	aaDP0W/0EkqoFrSLwjeUTR5XNVF/8CdlyJHvjq/
X-Received: by 2002:a05:620a:1a22:b0:93c:664e:e205 with SMTP id af79cd13be3=
57-93cb59f3452mr1229114685a.11.1790949151672;
        Fri, 02 Oct 2026 06:52:31 -0700 (PDT)
Return-Path: gemini.s.lumina@gmail.com
Received: from 166.1.168.192.in-addr.arpa ([108.18.189.27])
        by smtp.gmail.com with ESMTPSA id af79cd13be357-93cca2ed5e2sm222067=
785a.47.2026.10.02.06.52.30
        for <noreply@github.com>
        (version=3DTLS1_2 cipher=3DECDHE-ECDSA-CHACHA20-POLY1305 bits=3D256=
/256);
        Fri, 02 Oct 2026 06:52:31 -0700 (PDT)
Message-ID: <6abfb71f.fc1023d6.c1b67.e9ed@mx.google.com>
Date: Fri, 02 Oct 2026 06:52:31 -0700 (PDT)
From: gemini.s.lumina@gmail.com
To: Lindsay <noreply@github.com>
Subject: [EXTERNAL] Re: LindsayRidgeway invited you to
 LindsayRidgeway/llm-symposium
Content-Type: text/plain; charset=3D"utf-8"
Content-Transfer-Encoding: quoted-printable
MIME-Version: 1.0
X-EOPAttributedMessage: 0
X-EOPTenantAttributedMessage: 72f988bf-86f1-41af-91ab-2d7cd011db47:0
X-MS-PublicTrafficType: Email
X-MS-TrafficTypeDiagnostic: SJ1PEPF0000231F:EE_|PH7PR21MB3069:EE_
X-MS-Office365-Filtering-Correlation-Id: 9a599b8a-192f-4507-20e8-08df208c68=
7d
X-MS-Exchange-AtpMessageProperties: SA|SL
X-MS-Exchange-EnableFirstContactSafetyTip: enable
X-O365-Sonar-Daas-Pilot: True
X-Forefront-Antispam-Report:
	CIP:2607:f8b0:4864:20::741;CTRY:;LANG:en;SCL:5;SRV:;IPV:NLI;SFV:SPM;H:mail=
-qk1-x741.google.com;PTR:mail-qk1-x741.google.com;CAT:SPM;SFS:(13230040)(70=
4162211799003)(260918215300599003)(43022699015)(7093399015)(260918224100599=
003)(4128699003)(19002099009)(6123799006)(16102099003)(18002099003)(5511209=
9003)(10067099003)(56012099006)(5063699009)(11063799006);DIR:INB;
X-Microsoft-Antispam:
	BCL:0;ARA:13230040|704162211799003|260918215300599003|43022699015|70933990=
15|260918224100599003|4128699003|19002099009|6123799006|16102099003|1800209=
9003|55112099003|10067099003|56012099006|5063699009|11063799006;
X-Microsoft-Antispam-Message-Info:
	=3D?utf-8?B?Z1FsQnRFM0Y1TUw4RDJuM3BvWjhuZVA4MDJ1dWI2U2lzbW14dFpPYk1GcWo1?=
=3D
 =3D?utf-8?B?NjF0WEdGY21GWWRmdUxXYWFGaGtzRWIzaUlJTkxFNWlZcExHcVBDb21UZmVF?=
=3D
 =3D?utf-8?B?bXV6VFBNS3BQVzE0TUcrSEVlRHY4c0ttRWFac3VhL0dST2Z2amY2a3MzS3RB?=
=3D
 =3D?utf-8?B?VTk1ZUhTZVRhSmdScW5QV1JCOXh5NDByaTlXWW5ieU1ibnZrN0NWakd4djY5?=
=3D
 =3D?utf-8?B?OU5wcTF2K1BDMmd5M1dTRHRJaHdhTnpEUFRhNEVKUTJKVU1IbGtRS0NwMDBo?=
=3D
 =3D?utf-8?B?R01OQXoxZnJqbEpQZ2xvRU5YNTRvZFZRTUgvRURxb1g5TER2MW9XbVhJeTNT?=
=3D
 =3D?utf-8?B?cTR2MWpzNDU0a0F6RTlnWDhzZWRPdTZEZ2wxLzk1VGlnOTdDWE9pYTg0NlpL?=
=3D
 =3D?utf-8?B?eVVtdGdtUWZmMk82M01HUStBRy9QYU56TXk0eVlZaGFtcDVGN09YNFl5dlhv?=
=3D
 =3D?utf-8?B?dTR1OU9KQTNkT0wzelh4QkplYmRROGZXT05ubmF2Mm9KWnhBZ2dvTml6ZzdV?=
=3D
 =3D?utf-8?B?d09TdTlBZWsrM1RpVVYrR3NoTk9lL0JKZ3BXdno1TjE4SUI3WTJNdFVOY1Zl?=
=3D
 =3D?utf-8?B?ek15cHpBMHFTSXZvamI4Z1Z6VTA3T2lUMk5ZUUplNHk3ZDZ4M1dVS0Vheitu?=
=3D
 =3D?utf-8?B?blh3QVZ1eU5NbmpnZFE5WGc5aUhGZEhrdVoxeFIwcEVRcXlWUFJVYUZCWUVr?=
=3D
 =3D?utf-8?B?V1hEMVFJYnZzNzhsdkdhTDVVam1ySFhRUWh3ZE0xTkZHakIrb2V1NUIrWlFi?=
=3D
 =3D?utf-8?B?MnBkc3pXMWdETzlybitEWHkya3Q0anJnTGZoSk56RE1MZUxHVTFvdks4MS9s?=
=3D
 =3D?utf-8?B?eTIxWDhSMng2cHpFRVpyNEQ5U011Qzh3UmlXUkpFKy9jekMyV2xPcUkvR1ZT?=
=3D
 =3D?utf-8?B?TTJvYUliSE9KNjBaMkZadTA1TEc3WUNJZjlDdS83a2dCVnFUaDF4aDZkRGRs?=
=3D
 =3D?utf-8?B?UldkanVXTk9sYXpSTGcyYVkrWTRRZzZaa2JmOW53QnVucHVwakVJK1Zlais4?=
=3D
 =3D?utf-8?B?bFJyK1Nod0t4aXR6OXhpN1lsOG51ZlpSckZWajZxejRnKytZUWZTTkpMNWV6?=
=3D
 =3D?utf-8?B?Q3RqR1JmdnVmNmkzU3krMkEwY1EwWWoyVjNENXpiWFRaNjRVQm9RUnE2cjhu?=
=3D
 =3D?utf-8?B?bzdGbXdkRUloZW5ER2dCdFMvSFF1N2N6Z2RmWDlhaHFXbGpTR0VHL3VVVlhl?=
=3D
 =3D?utf-8?B?ek9OOU8xcXI0V2JyVk1nOXF1QWxkV0xlZ1pLck4vZlhYNGZDaFVGemU0U3B4?=
=3D
 =3D?utf-8?B?dzgxUlhNNTJiaG5Mb0JFSUxwZWlKdnB1U0xuNGxzWTd6UThQNkc3ZTJVWHVR?=
=3D
 =3D?utf-8?B?QmhLd09vS0tWVWhXdHFrdWduNGNscVdQeFV6eEhXS0RtWlIzb1hHRjlhT1ox?=
=3D
 =3D?utf-8?B?WlRyNDJxQkVLaVRrR3RvdHNjQ05JSVlTQ3AwWTFlaDdKRFZia0ViM21JSVFi?=
=3D
 =3D?utf-8?B?azFlczAreUZLSlBVdDJYS0RXWHNhVytyc0NnY1J3bWNVdjhXRmJSTWY5VjIz?=
=3D
 =3D?utf-8?B?Vi9XZzQ1QUFzeU9UZUpTbTFxQzJud2tlZXduYk9qMG84Ny9DQlpoN0U0cFBw?=
=3D
 =3D?utf-8?B?UGw0UjRLTUlMekk2Y2xuN1Ryd2trSEdyNzVwSlppcEd3REFJMHRNTk96cmtp?=
=3D
 =3D?utf-8?B?UVEvYXF3b3lLSC9wOEJKK2tWeFBZS3VPdG1udGpwaFBlUDZBSkVKcnY2MUtx?=
=3D
 =3D?utf-8?B?K0VPdEk1UnBrSStvbjMzUkRoWW5kWThkbk95ZUUzc1pHdmRReFYrRjIyNkMw?=
=3D
 =3D?utf-8?B?Q01EUERGSThHYzJTMjE3N2JsTGRuNE1GQ0xlRnNPVUd2RzMyRzVxWWtqdkxy?=
=3D
 =3D?utf-8?B?UTBBS2drZXNKcVZzenhkY3NEOVRNSU9ZMkZndDN1TWJBdDd6WnQ4TERmaE9I?=
=3D
 =3D?utf-8?B?a0ErUTVKQm5rZEhOdHBKdnkxR0J4VE1ueEYvVEVaZVFVZVVnUTc2ZXo5QVlo?=
=3D
 =3D?utf-8?B?SDFkeE9kU1MxNDhzRkhFYi9oTEIrYUZnVmRlQW4zZXNZUldDMkxJSnBET3lB?=
=3D
 =3D?utf-8?B?TFFBaWROZjhwOVplNzdrNjRrRFN5QWF2ZWZrSU5oVUVLckthVnc3NU1LRDUv?=
=3D
 =3D?utf-8?B?K3dnZ3JYT2ZSaUp5ZlB3dEdGZURmaEVHaUREczZVSi9kUkRteWtSRkxUZXJm?=
=3D
 =3D?utf-8?B?NktZbWNLZFc5YWJZQ01MaGgvbnhnRnh6MUVjVmc1L2lpM2VLUy9nTjg5Sm9J?=
=3D
 =3D?utf-8?B?bU1uVTAxdER4MXNDL3lzOCtlUXJuc1pYeEFsd2puVkZ3aEU1dm4zcjFGelRX?=
=3D
 =3D?utf-8?B?REFyd1RvN3FsQWVkQ1hhckVXaHk4TDcySVVGcDhkeS8xSHFXNjQ2K3FNMi9U?=
=3D
 =3D?utf-8?B?aVVhNEFIdXM5NHhYZVF2bmE3K2ozV0p1QmxDWFgxdk1ESmdoaGExNmpkWHpT?=
=3D
 =3D?utf-8?B?bkZtUGkvMlpWelYwSUoydUpLWGsweklidnQ0ZmhuMGo5Q3Z0WElDYzJPRUtP?=
=3D
 =3D?utf-8?B?TVN1UVpoLzM1MFpGT0Y5RUtLazB6MCtHM2xTSmd4THNYL3d3NTNaV0NZSTMy?=
=3D
 =3D?utf-8?B?L1Z6YnBVb2VBcWc0aHZlTVhQWHlaNjZoRVljZmQvUGVFNTUzTE1SU0E0UWhk?=
=3D
 =3D?utf-8?B?M1F4cGlZM1hWOVdWK3JmR3o0N3RHWWNSUTQzTEZuSUZFQkUxWjJybXMzMiti?=
=3D
 =3D?utf-8?B?YmZrZ21US240eXkxQ0NnaDhGQkswdU12OHIyWlgvRDRCQStiL0d6K1ZLUVhH?=
=3D
 =3D?utf-8?B?RG5xY2lUR1VYZmVzbWRTN3JtZURURWR4WXhpNFF3bTZWTWVmUVFjNUlocUQw?=
=3D
 =3D?utf-8?B?N0ZzdXVkcldmdkxHZXo3b2hnL1dFeDFVUU8rQ2VMR3FhSlQ4VnA2cnhnczIr?=
=3D
 =3D?utf-8?B?UHdycS9aVTVMWUprOEh1SUNsdFVMQmVxK2hZcGdXWUY5cy9uc0dPRHJhUS8x?=
=3D
 =3D?utf-8?B?ZU9FZzRtYmZqUnd2YVVmelYzYW8xMmpiK1Jzd0xDQWJ6amQrbE1nQ0JLRGxt?=
=3D
 =3D?utf-8?B?QkRhWW5DdzllWmRPTlphSVFxbjdPZ1R5dUppNVl6WThqcCtZTmhWUGFsV085?=
=3D
 =3D?utf-8?B?andLU3NWY0V2WmRnOXYvek1XUUxDdS9KTkEzM1RpZEY2cHZyZVFFSFdidDJ0?=
=3D
 =3D?utf-8?B?TWNhZmtYVGJHZ1VZMFpQajVEcGVCZ21zWU8vdk1QQTF4T3pqem4wZWlhYWlJ?=
=3D
 =3D?utf-8?B?WjhKUjhrUjBPc1Z6MU5zSVpzVk1ac3ZLQUxiSGtFTWZ1V3A0MUFGT05JR2V1?=
=3D
 =3D?utf-8?B?dVIrWG1qcW14Z1lmNUtuTjBmMEhCZ1ZHczBqbEhva0hnMmhISzNra1RuQmk2?=
=3D
 =3D?utf-8?B?clFPdkZJcFVHajUyTWxORERFQmhLeHc4TmtlUUwvMkw4UmlCYzhxRUZ1UnQy?=
=3D
 =3D?utf-8?B?Sys3LzBoTStYaXB1K2lOMU5TdzAzUSthMXhucUtFKzRmZ1NiVHZNdVJKSlFw?=
=3D
 =3D?utf-8?B?ZEpOUmM0UnVxWnBUQ2hkd24zQk5xRFdNMXUrNlVSMWVuMHYzWENDbThNOWo4?=
=3D
 =3D?utf-8?B?eFVabWp6cXM0TDd5ZFpjbXJLamFFRTIyQjZYS24rdEFjQlVFZGNlL3RVSklW?=
=3D
 =3D?utf-8?B?MmZ3R0VZMmhMOVR0emJxZExvVDlRc1liVlFsY3dyK2hiUTZUZUFoVHBkNmI1?=
=3D
 =3D?utf-8?B?eUg0OTVwVUZ3anBkUzAzVGdQU2dCSW9OZEdWNGl4MEwxdEprN1laUThEV2Vo?=
=3D
 =3D?utf-8?B?bnFCak9JMi9xNW96MUk1bFNTL0VBcmZhd3g3WC82ckNCYjhKMDJMQk9mSzNU?=
=3D
 =3D?utf-8?B?ZnpOdHlibFd5VFlTMWV0MmFvWXRKc0tUajQzMWZCd09nemtncWlMOEsyOC9J?=
=3D
 =3D?utf-8?B?NTBBWXRRdmlFYnJOUks2ZW5iUmZDYkovRVFJbUJFUjhTQ1E0NTdLM0V6SnBa?=
=3D
 =3D?utf-8?B?dE9JbnY0VFhNcWJQYU1MRFJwam9zOElhYkhwemVKOWtOa3Q3T2Npb2ovSndZ?=
=3D
 =3D?utf-8?B?YUt2QkhlSjJaZXVTWHIyWnBScE53bFY4c295c3JRWlZZcFg5aTMzV1A5Qmxz?=
=3D
 =3D?utf-8?B?b3FGZ2xTUTRNU1BKTFVnSHhxZzVRUWNCdkJuTzhVR2dWbkZ6ZXdVV2IxeWFy?=
=3D
 =3D?utf-8?B?RGdOeVA2OUhUN2lURFI4YW9QeU11eVNiVThkd3JhcStIMzY5dmFqeEVJY0Fw?=
=3D
 =3D?utf-8?B?SHptU2VXSGpRMnF5V2lBQUpjUG52L3Q2N3VoSmlzYzZVRlF5eEVnMTArV3po?=
=3D
 =3D?utf-8?B?TW41SEs5Z0J3dC9lU2ljbEFiTW9GdUhxY2xqbGsrRGFMbnBwcUtoOFpPWDN4?=
=3D
 =3D?utf-8?B?TUVOVEdBMndra0pwNGl6cjVTcDI0bzVoVFdvK091amNxM2RpZjdhZEphNU0z?=
=3D
 =3D?utf-8?B?VXI1ZytWQjFWL2REdGN0OXU4VEd0aGRwNm1ncXpIb0RFampHbkswUTgwWGtH?=
=3D
 =3D?utf-8?B?NGxUYnBjNmE5TEk0QTBJZWE2elJSMFBKbFF1NExRWHQ1bXA4SnY2bHNQTUxW?=
=3D
 =3D?utf-8?Q?vTOrH?=3D
X-Exchange-RoutingPolicyChecked:
	hdUurSn98dgq1TaVziSApcMzKPHw4nNxremQOMDCA0El2rPMIj7zuqz6yj/afPaBAp92VLd8Jl=
Wy1AzE7n9KGIA2jowW3AgZ2ZQABGUGl5pgumIvXRA5yTNEDbAT7hNlMLhnh4RpfGuKgktMfZlqU=
JWndanqHCQlAjYi4MFO33UHmfsxbCM742oTZovHMeRArwow6+m2A8ezsvvunRFeXYp0ZLp/ARre=
V8pqMxrMHB24iGET1uVAY4iIewR73K6vFaxbAzBSac2nMHvtM0WSIGXSeN+6vK3sKmEKgq3ltT9=
S8Nm/Zef9kgprw2BKgntm4WhoomAjjf6SAAMPVJ107A=3D=3D
X-OriginatorOrg: microsoft.onmicrosoft.com
X-MS-Exchange-CrossTenant-OriginalArrivalTime: 02 Oct 2026 13:52:32.9571
 (UTC)
X-MS-Exchange-CrossTenant-Network-Message-Id: 9a599b8a-192f-4507-20e8-08df2=
08c687d
X-MS-Exchange-CrossTenant-Id: 72f988bf-86f1-41af-91ab-2d7cd011db47
X-MS-Exchange-CrossTenant-AuthSource:
	SJ1PEPF0000231F.namprd03.prod.outlook.com
X-MS-Exchange-CrossTenant-AuthAs: Anonymous
X-MS-Exchange-CrossTenant-FromEntityHeader: Internet
X-MS-Exchange-Transport-CrossTenantHeadersStamped: PH7PR21MB3069
