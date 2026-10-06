# Delivery failure — 2026-10-06-142949 (desi)

- From: Mail Delivery Subsystem <mailer-daemon@googlemail.com>
- Date: Fri, 02 Oct 2026 08:08:33 -0700 (PDT)
- Subject: Delivery Status Notification (Failure)
- Message-ID: <6abfc8f1.22f06866.2e092a.2e1f.GMR@mx.google.com>

---

** Message blocked **

Your message to noreply@github.com has been blocked. See technical details below for more information.

Learn more here: https://support.google.com/a/answer/172179

The response from the recipient enterprise administrator was:
The user or domain that you are sending to (or from) has a policy that prohibited the mail that you sent. Please contact your domain administrator for further details. For more information, go to https://support.google.com/a/answer/172179



8-88af476a614mr3220515b3a.17.1790953712370;
        Fri, 02 Oct 2026 08:08:32 -0700 (PDT)
ARC-Seal: i=3D2; a=3Drsa-sha256; t=3D1790953712; cv=3Dpass;
        d=3Dgoogle.com; s=3Darc-20260327;
        b=3DoMAmYOelVSpLje0vWfdGHWs7sCSBSbPulIgUmpGT75o8WB8SZoCqo1Oe4BRsSue=
pin
         UiTfvBjR7cLTccfVY9J2UAm+I7ziOYEQqprqrW6QbgocBfikOpAvOYroyDveAPv6Il=
PV
         Q7Dvp7SVfUe4fueYI/zjDjzKlYOAiTWGmuDX0o3IWZdyL9/vko0KbTwfzZpRxvCI4T=
jt
         yDDTAD5Cw7cWkQDnp7mMYnks12ZC16uXJ4zpspHhi0Pn2J/eiE/8+BnrPsEUsw3Lsy=
Jw
         zZ3eewrWOJnsJdj/VRkHwWH3Jofi28eb6P3TATGVxo3uEf2jsJKjyh2gpYDNFkUCwT=
eU
         QfZw=3D=3D
ARC-Message-Signature: i=3D2; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dgoog=
le.com; s=3Darc-20260327;
        h=3Dmime-version:content-transfer-encoding:subject:to:from:date
         :message-id:dkim-signature;
        bh=3DR1v98nxgJur0Y4GWFM2v4CPPsiHK4CYxf5Kapq+0uRQ=3D;
        fh=3DPJ8u2s4MkgJOcYTBmnXg+3QstaBJeBvZbOkML/66SwU=3D;
        b=3DCNIfTm0TXdGoKh5AbODf0E9/chqnU2Oss6s/x4ndF2iFWXfGeIcDf/0oNk03UhD=
1UR
         zXamAe1/lLZ7BOpllmCe7aWw6InYWDEyVn5MWi6hoZnplgUD+JcHFOphV1uGCrZaDs=
kv
         KgMGEq1Vby9VAyYyDSSGH+mjnFQb07JKZTOdz2xX0fgdsE7RE7jCEPkGukeWnlR+Kg=
GV
         iTJzLqdwlhoG6dxZJuYOb0rlv6yl6F198v6cXiQJdIddShfJdO7MIM3EN8c4/OD9p0=
22
         Vo4T5+GHA4vd15ZHwHQdi3RRiPkr0Z3Wpi2R2A6pJv+mACLz6YNLsTOEXHkvJVoxCs=
2q
         s56A=3D=3D;
        dara=3Dgoogle.com
ARC-Authentication-Results: i=3D2; mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3Dhzh=
oFgTS;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning desi.s.amigo@gma=
il.com does not designate 2a01:111:f403:c107::9 as permitted sender) smtp.m=
ailfrom=3Ddesi.s.amigo@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
Return-Path: <desi.s.amigo@gmail.com>
Received: from PH7PR06CU001.outbound.protection.outlook.com (mail-westus3az=
lp170100009.outbound.protection.outlook.com. [2a01:111:f403:c107::9])
        by mx.google.com with ESMTPS id d2e1a72fcca58-88b0d93807csi5178727b=
3a.167.2026.10.02.08.08.32
        for <noreply@github.com>
        (version=3DTLS1_3 cipher=3DTLS_AES_256_GCM_SHA384 bits=3D256/256);
        Fri, 02 Oct 2026 08:08:32 -0700 (PDT)
Received-SPF: softfail (google.com: domain of transitioning desi.s.amigo@gm=
ail.com does not designate 2a01:111:f403:c107::9 as permitted sender) clien=
t-ip=3D2a01:111:f403:c107::9;
Authentication-Results: mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3Dhzh=
oFgTS;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning desi.s.amigo@gma=
il.com does not designate 2a01:111:f403:c107::9 as permitted sender) smtp.m=
ailfrom=3Ddesi.s.amigo@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
ARC-Seal: i=3D1; a=3Drsa-sha256; s=3Darcselector10001; d=3Dmicrosoft.com; c=
v=3Dnone;
 b=3DhqRmex/8gaSot1wVu8h4+yDBUO0FhJH/ifSvIFtigtcXj9TCa91mvmrcchlgd4E6BXtcv9=
eb+LgQpPpHaArQ2zwc7Rp/PWGQr/Xfp6DWQfOMWfDUPHJROe/fW4OF+7062bKEiFJTKoYfPeYRu=
+hjs+PRtd+PjpdbiYhumN/UNjxRNCd+FsUYAM2WujmWg0J82ZsTS95Ol2JTiLxfpeoXT0snzkbL=
nQZc+xOVQ92PxItsY1H7SumhazwWTksfGX1jxHw2SSy9kR/8DScP7yjN1QQHJv5r3PXICGlpgcN=
nD4V2wE3o/GSFdo2Rl7JcocI0Y5dlR83zdFHO0Zl8rE6fow=3D=3D
ARC-Message-Signature: i=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dmicr=
osoft.com;
 s=3Darcselector10001;
 h=3DFrom:Date:Subject:Message-ID:Content-Type:MIME-Version:X-MS-Exchange-A=
ntiSpam-MessageData-ChunkCount:X-MS-Exchange-AntiSpam-MessageData-0:X-MS-Ex=
change-AntiSpam-MessageData-1;
 bh=3DR1v98nxgJur0Y4GWFM2v4CPPsiHK4CYxf5Kapq+0uRQ=3D;
 b=3Df4SINH4P4yeVpFht7AwbkRVZ8z3CFAAHNNhV8QQqvavJyi/tLp6pOAmFIY+dj41WebX983=
UnHnxPLvtOutB0N9vQRN05AlXIsqQaMuRG0ZkqXVxlRCe7weazaW0xciCA1NK19A9fSsEaGZYVN=
1tzX4106F3jCDbiKN2HZb50FIL/dWJCUT0cPbGr4a3oSB6y7za4hVO+DLDRa5Z8bBzB0O3vjpQM=
GLHsK12NaMu/uucQKajtU6z2F+/yhMcYrkGPim8dV0sjnRfiHNd+ffqph6zV0KoQy3vVIg47pDc=
akje8Q6hF5yQ3rlegf+3VOxVKIaQbYJxAWFtqXT+v0DBhlg=3D=3D
ARC-Authentication-Results: i=3D1; mx.microsoft.com 1; spf=3Dpass (sender i=
p is
 2607:f8b0:4864:34::) smtp.rcpttodomain=3Dgithub.com smtp.mailfrom=3Dgmail.=
com;
 dmarc=3Dpass (p=3Dnone sp=3Dquarantine pct=3D100) action=3Dnone header.fro=
m=3Dgmail.com;
 dkim=3Dpass (signature was verified) header.d=3Dgmail.com; arc=3Dnone (0)
Received: from MW4PR03CA0164.namprd03.prod.outlook.com (2603:10b6:303:8d::1=
9)
 by LV0PR21MB6142.namprd21.prod.outlook.com (2603:10b6:408:332::8) with
 Microsoft SMTP Server (version=3DTLS1_2,
 cipher=3DTLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384) id 15.21.496.13; Fri, 2 Oc=
t
 2026 15:08:29 +0000
Received: from MWH0EPF000C6192.namprd02.prod.outlook.com
 (2603:10b6:303:8d:cafe::a4) by MW4PR03CA0164.outlook.office365.com
 (2603:10b6:303:8d::19) with Microsoft SMTP Server (version=3DTLS1_3,
 cipher=3DTLS_AES_256_GCM_SHA384) id 15.21.472.18 via Frontend Transport; F=
ri, 2
 Oct 2026 15:08:28 +0000
Authentication-Results: mx.microsoft.com 1; spf=3Dpass (sender IP is
 2607:f8b0:4864:34::) smtp.mailfrom=3Dgmail.com; dkim=3Dpass (signature was
 verified) header.d=3Dgmail.com;dmarc=3Dpass action=3Dnone
 header.from=3Dgmail.com;compauth=3Dpass reason=3D100
Received-SPF: Pass (protection.outlook.com: domain of gmail.com designates
 2607:f8b0:4864:34:: as permitted sender) receiver=3Dprotection.outlook.com=
;
 client-ip=3D2607:f8b0:4864:34::; helo=3Dmail-qk2-x00.google.com; pr=3DC
Received: from mail-qk2-x00.google.com (2607:f8b0:4864:34::) by
 MWH0EPF000C6192.mail.protection.outlook.com (2603:10b6:30f:fff5::476) with
 Microsoft SMTP Server (version=3DTLS1_3, cipher=3DTLS_AES_256_GCM_SHA384) =
id
 15.21.472.14 via Frontend Transport; Fri, 2 Oct 2026 15:08:28 +0000
Received: by mail-qk2-x00.google.com with SMTP id af79cd13be357-93cc61ea982=
so59209285a.0
        for <noreply@github.com>; Fri, 02 Oct 2026 08:08:28 -0700 (PDT)
DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3Dgmail.com; s=3D20251104; t=3D1790953707; x=3D1791558507; darn=
=3Dgithub.com;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:from:to:cc:subject:date:message-id:reply-to
         :content-type;
        bh=3DR1v98nxgJur0Y4GWFM2v4CPPsiHK4CYxf5Kapq+0uRQ=3D;
        b=3DhzhoFgTS8RvgkOiRF6Etq9Tzfs7gVTgHZGn53g7yUSSWwtDcqGCmQQZOBh2dzF2=
+kL
         GXnL5322D4nEjt7/CCyBUKVgXRfQ89dVymYYKy1ohs3QxCL4BQX7RgkGEkvRHm2zHB=
cf
         I3L0b6c/RFmV+IvvNKyHhNSLlhrHjsFir/ee+gG1usUn5EE5Ye3dlQss0cupyyiKaP=
rn
         j2skQfLQ1mqyXgH3ehd32q5fzDsSQo10ROnf+yGX7+Pp7cqLfl/sIfCGpD62XvvP+R=
eI
         7Gvfdf/7mbl0G6OWMgD+fOxf0HiKN09bORmcb23G0axrMLTqSUXsEaAyI/rK3HSdSg=
Ab
         AUMQ=3D=3D
X-Google-DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3D1e100.net; s=3D20260707; t=3D1790953707; x=3D1791558507;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:x-gm-gg:x-gm-message-state:from:to:cc:subject:dat=
e
         :message-id:reply-to:content-type;
        bh=3DR1v98nxgJur0Y4GWFM2v4CPPsiHK4CYxf5Kapq+0uRQ=3D;
        b=3Dvg9jS7vGIk760OqEAy6pIdV6MpuSSq8FTw1uOds8IRosOXc58cEThSvYve4Gdxo=
/0X
         hMIhww62BX+B5VL/UHxQjzmTr44kxUXmiB8md0JQ10N+/vnUT9Kkv7n1BK60USdjIJ=
lJ
         vny9IZ1pwWByoCo1laO8aklZaNTerz+8gSBIgLoJJOZGniQxkJsI6EeulU8ufSqW27=
W7
         UzESeWtJtSi1ztZf2Au47iQJ5VVL+nYgZoqefwuVI0l6VW35cDCgBQWI7oMHL/y4Ys=
xT
         I30GRbpnoYGr3JZrdo+sMGEwO/HD2YUqavDQMvhP2n+WQ1IrCFdFVp7PopJONuMrMq=
g2
         /CsA=3D=3D
X-Gm-Message-State: AFuF++nxGrqVkQ97yiazb1hCQuW1SWrV9CCTvq0FMDDa9yuj8N4jmbB=
X
	5Pao/Kcv6atDaYMPxTxLETF39SMliGicyIXSt7Nnf1PMB/rMOlMRkLQ9c48YRM+IWjMGG1rS
X-Gm-Gg: AYBFou0hDU3yzQTBA1eNCzlAjtNVPOs5ARMeD4jp3gVeIGxsim5Az+OL0WATjdhkkF=
c
	QnjtP0cOmJPixScN/ES0PBNM9ZHsrOnuBuRcnJhFdjGbVsTtX3ceGppynQXlwpdc4RpM7PM90M=
V
	ukmyEisxZox5OrbPfW8sifVeIzIt+t0wZLUnAiXn+17Y8QPIfsnPb9BGxsUSXUcNXGLEEZ7qYc=
m
	xbxsFAA0b1qos9hSUfk/eeT0vUVFONBT1hg0dnkMu33gSvd06cL7w+lchUEqvlly3ErB99c1ld=
a
	aFAKo30QmTyFNXWYiAH0fITvFo41SIyqgSGMVT3P4VRGSlCkeXSmDi6j293k/iIIR4clZGDWKI=
e
	ckSCk3k9M95wCkhLxtb2T3LIxp7CcJWGY64YPeDdCvdGYNv7eIRsTFyuamqARn//tkU/uZhVhm=
Q
	qabPopqDZoEYXNBH3SaHRXxOPNf56v/RDRR+Wh1UvyHrAlgs9FdyTEfHNdNJQbXSX1G+uFsh6F=
F
	9hO+Jqq4l5zi7nZhct3M46NFMWIJjFL+Sw6t/B6oqeqxH70R1Nq1nl9Hh7w40cLlGSsKaMqRLv=
9
	PvOtxBMlPOIlemUt76DnNYKUQ/VUDaG/4aRG8KceLHg=3D
X-Received: by 2002:a05:620a:6f8a:10b0:93c:3862:9924 with SMTP id af79cd13b=
e357-93cf16e768emr379267285a.27.1790953707136;
        Fri, 02 Oct 2026 08:08:27 -0700 (PDT)
Return-Path: desi.s.amigo@gmail.com
Received: from 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.=
0.0.ip6.arpa ([2607:fb91:8cd:d559:55b2:89e0:8d22:76d3])
        by smtp.gmail.com with ESMTPSA id af79cd13be357-93cca2d361bsm241758=
585a.45.2026.10.02.08.08.25
        for <noreply@github.com>
        (version=3DTLS1_2 cipher=3DECDHE-ECDSA-CHACHA20-POLY1305 bits=3D256=
/256);
        Fri, 02 Oct 2026 08:08:26 -0700 (PDT)
Message-ID: <6abfc8ea.28a8237e.ac2cc.82cf@mx.google.com>
Date: Fri, 02 Oct 2026 08:08:26 -0700 (PDT)
From: desi.s.amigo@gmail.com
To: Lindsay <noreply@github.com>
Subject: [EXTERNAL] Re: LindsayRidgeway invited you to
 LindsayRidgeway/llm-symposium
Content-Type: text/plain; charset=3D"utf-8"
Content-Transfer-Encoding: quoted-printable
MIME-Version: 1.0
X-EOPAttributedMessage: 0
X-EOPTenantAttributedMessage: 72f988bf-86f1-41af-91ab-2d7cd011db47:0
X-MS-PublicTrafficType: Email
X-MS-TrafficTypeDiagnostic: MWH0EPF000C6192:EE_|LV0PR21MB6142:EE_
X-MS-Office365-Filtering-Correlation-Id: 42036b4f-3986-461f-d565-08df209703=
de
X-MS-Exchange-AtpMessageProperties: SA|SL
X-MS-Exchange-EnableFirstContactSafetyTip: enable
X-O365-Sonar-Daas-Pilot: True
X-Forefront-Antispam-Report:
	CIP:2607:f8b0:4864:34::;CTRY:;LANG:en;SCL:5;SRV:;IPV:NLI;SFV:SPM;H:mail-qk=
2-x00.google.com;PTR:mail-qk2-x00.google.com;CAT:SPM;SFS:(13230040)(7041622=
11799003)(260918215300599003)(260918224100599003)(43022699015)(7093399015)(=
6133799003)(18002099003)(16102099003)(55112099003)(10067099003)(6123799006)=
(19002099009)(4128699003)(56012099006)(5063699009)(11063799006);DIR:INB;
X-Microsoft-Antispam:
	BCL:0;ARA:13230040|704162211799003|260918215300599003|260918224100599003|4=
3022699015|7093399015|6133799003|18002099003|16102099003|55112099003|100670=
99003|6123799006|19002099009|4128699003|56012099006|5063699009|11063799006;
X-Microsoft-Antispam-Message-Info:
	=3D?utf-8?B?dngxMHA5NFd5ZERRT05PZmlTc2daaFRqYkhJZ29obkpvQjFITmJZU2ZKQjZS?=
=3D
 =3D?utf-8?B?UHIwZ0l5eTJkcnZvY0tsTTczMDF0MU9KcHdGZVJBTE9YODNnanZ4UEVZcTZx?=
=3D
 =3D?utf-8?B?eVo5OVdKcmhIcW5TY0ZiY2FNWVNHRzZudUlVYktOOTdiaDUvaFJFVTZrdDVs?=
=3D
 =3D?utf-8?B?TjVXQnlpNGFTWGpBS08zY1pHVHl0aEVMWlozcEg1eUlEbzZpTXNTVW4zVnZq?=
=3D
 =3D?utf-8?B?ZmtFN1ZzRy9seWJ1M0tob1lNRmJLY2drSWVRRnFUb2E0aHhsVFROVzNjMity?=
=3D
 =3D?utf-8?B?ZEpqWW1qR0VQK2NlWThiaUNPRmYwT0tVNC9sSi9JbENpSW1ZaGN4Lyszelhv?=
=3D
 =3D?utf-8?B?TGNtUVdGbFNhQVpoMWlvdkJZNDlBdkx2UVcvNk82N09GaGdkZHhqYkJibFpX?=
=3D
 =3D?utf-8?B?UkdaY2lNMENMTjYvL1FkYTFSNk1HMzMyVUw0QlhiRE45emZ1TDN4YUNRZGxF?=
=3D
 =3D?utf-8?B?em1EekRETFdhOWZBeXUzNGtRMzlCTlE5MTIxY01yTGgxOUp0U3haRjB5aDNX?=
=3D
 =3D?utf-8?B?NUtJT1o5dUpiS2p5Z3BWK2dWa1l2ZDJrTHV3cHpIRk1CK2g0Q2VETDV1czVo?=
=3D
 =3D?utf-8?B?M3hKbDBvNGVaVTNzU05vdmphQTI1WW5zMW1xSldqczdUWkQySXJTd24yWXUx?=
=3D
 =3D?utf-8?B?UEtpU3pmQkR6M1EzNFovWmxQcEZ2bWowb0JLT3FmcnV3b0lIdlJ6dFlBUzlZ?=
=3D
 =3D?utf-8?B?dFZDMWUrVjFwZ3FUN0ZjZnlwMGV6UENSc29wVHF2bk85K3U2SjY4and2MWov?=
=3D
 =3D?utf-8?B?b1ZLTURQZ1FNWjFDK3M4S0RkRFFCV3VsMjNVOWdObjE2RkNUUm0xaCtEMkZJ?=
=3D
 =3D?utf-8?B?OVRCSlEwWjBWUWNPWEJheTZLQWJ6bE55RHhxanZvVk9ETUhKcithMDJ4VWtm?=
=3D
 =3D?utf-8?B?U2trakMzM0VXakc2SlBQY1YwQnRFV21mVEg5WVYrUFhSOTFPeTJYTURYWUM5?=
=3D
 =3D?utf-8?B?NkQxbHlta3E0RTdHa2pESmRHc0NVZTBlcGE2dUx6WjNSajVXL1VXbmc0U2la?=
=3D
 =3D?utf-8?B?WUxwZ0RVVEZyNERYaEFqb3BzMmN0L3MyNDk0Y2ZGUUorTUljbkY4dW9CSjhS?=
=3D
 =3D?utf-8?B?K1ppaDY0K0NTZGZGZkJVclNMN1EvUUVDcHNHYytVcXpUQTBoR1RPZVhWNEhC?=
=3D
 =3D?utf-8?B?YjhVOGRtK2s2TXQ5SzhNSm1DZE4wZmRHcFhTMGZaTEZBMk1DUW81bFVTV3dO?=
=3D
 =3D?utf-8?B?TDZCUUJ3ekNQeDlmMXc3UlNxaDlUSlpQcm02cnR5Tk9LdWR3bFo2dXVQWlNr?=
=3D
 =3D?utf-8?B?OU1LdkRZVXR3UFArNVl0TmZwTmp5S0RJMFdqU3B0bDc2dFZ2SDVQTXVyQUtq?=
=3D
 =3D?utf-8?B?QXdxREdUeXh2L3RERDVGUzdwd3VsUVdiNkV5ZDQyY2g4djA2RDY0Y21udXFw?=
=3D
 =3D?utf-8?B?ZzN6UUx4dFdkNU1iaElGYjIwY3RBNmpvdVpicEtTZUU1RXBXdEg2cmZiMW0r?=
=3D
 =3D?utf-8?B?bC9UU2ZSQys1alJMVEp5SFhFUS9OaXRUOGpZd1hrT0pHQVNPc3RpOFRtcVc4?=
=3D
 =3D?utf-8?B?M09Rd21KeHJscVVIR0tKb3pNUG5Fa2JoajhvYkViZ1JWdExLUWptRkdKSzc0?=
=3D
 =3D?utf-8?B?RDNxOTNpZy8yOVRmSGFScDhBODc1aWl1V0pmMm1iRWtDSzdXUjE2T2tJaFhq?=
=3D
 =3D?utf-8?B?QlFvbk00TUtxcWZZWTVvd3BsZkFodCt3V0pUQ1JSSCsrZWkvOUg4VXdnVHAx?=
=3D
 =3D?utf-8?B?WFhUbVJCY0lHZjQxTDl6WTZqSXpYNlpueDZwVUYyREpwS1hQR1AydlA0THBB?=
=3D
 =3D?utf-8?B?QlRwM1NWQW9uZ051RHRjTDdzMUU5UEpCNWpGK2lDVmg2ZlFUWFREZXlZKzZ4?=
=3D
 =3D?utf-8?B?UlhDemEwMnhYRkdVVEhnYnlheEprQlMxOUpydDllM3djVXNtR3lVc0hoVWxD?=
=3D
 =3D?utf-8?B?eU9jRkZ4V2JkaytaVXR6ZmZhSDhJZmlhUDdydHZUS3Bpb1R2cnVSOTMrSEd0?=
=3D
 =3D?utf-8?B?U2lZMjBGeElTek00aHlRUzZEQzNQbzMwbmNFalRER3VqQlRPQjR0Qnp6LzhQ?=
=3D
 =3D?utf-8?B?alo2WnFydDZZVTRDUnNkREtBVEoyeHZkbGFkUUd2N29NZFdjb296d1oybjRs?=
=3D
 =3D?utf-8?B?YWQ1V3hSWWkvakQvd1M2bi9hcWdDTGhXOEhPS21iVjdRV2lMSFcya1JPeHJt?=
=3D
 =3D?utf-8?B?bnA5cmQ5ZlZHVHFKUGwxK1VDWHNxR29wMzQwR0FXbkp6aFNsMHgxelhWdGo4?=
=3D
 =3D?utf-8?B?U3ZGMWlkRkFzaGgxT0dKZXNGOEZQbXlWNy9BM2RTcXU4TDBkREtkTU1tTDZ0?=
=3D
 =3D?utf-8?B?Tmk5OGg1SHdGZzBTc2VrdmpYeWhDYUtUa0RLVlcrbnlCRXI1cHRmNUFFQ0Ny?=
=3D
 =3D?utf-8?B?YmdzMkpqOTZPUE0xT1FoeWsvWXNnTU1yMUNhVjh2NG4zNVMzejNObjdSS3k4?=
=3D
 =3D?utf-8?B?WVR5ZURaSnYva3lKaC9oQTE3M0FCUTdSTFMvU2JobFYva3RrdkJGYzhTUG11?=
=3D
 =3D?utf-8?B?YktodndHdkZ6aVE4V2I5KzV4Kzd4eklxOE4yeHUrdmx5d3N2TGQzRXEzMnVy?=
=3D
 =3D?utf-8?B?UUl0VHZZbjhvOE13T20vc2p0V2FyUlErcHZETUtDUTJnM2tYTnFIMCtjVVhK?=
=3D
 =3D?utf-8?B?TFAxWmtobzIyMmMreCtSemNIbE40amM5cWF2YVhxYXBVd203T29oV1RkQk9r?=
=3D
 =3D?utf-8?B?MU1hcUszS1dmRzlDNFpRU3YzV2R3TitFYXVLWHowNG1nbWsvdmE3ZW1LN3FZ?=
=3D
 =3D?utf-8?B?cVdEcmh3UHVLUW1sUzF5cEpLcTZQbjU1c0ZTa1B3UHZHZWd4aWpIZ29YU2Yz?=
=3D
 =3D?utf-8?B?UEZYRklaV25DNTF4NVdXY3NLa2EzV0Q4Kyt5ZWszTlJBOGxQQnFKMk9qL1pB?=
=3D
 =3D?utf-8?B?UWZBTENNOFg2azBxZngvOExkdEM1MkNVb3dKVkxvcmZmdWFIYVkvSzV0SnY4?=
=3D
 =3D?utf-8?B?Lyt4YSt1U2JGRDZ6b1pPY1RqVHFtU0FRWVFIL0t0OTlQM2poeXBveUczcnlJ?=
=3D
 =3D?utf-8?B?Tzhscm85Y3F5Nnc0dlppamllUFBZcSt3eFFvdWl5TjNSdlVQM3Vjb2Zmc3Jm?=
=3D
 =3D?utf-8?B?cFgrTERiYjBTYzJsVHVZMyt3QnlveDdpOWFuZE1MVVpxcUZOSStyR0pRSUZT?=
=3D
 =3D?utf-8?B?TjFDQUd5a2lLOEhPQ0FOZmUwdGRuajJhWmZpNkttWFNHS3JMRWdFZXpJR0VJ?=
=3D
 =3D?utf-8?B?Zkd3c1lwUU1tN0gwU0VEcDZIQmRqQ3Z1TnUvaVNaVXVQU3U2anhEM1JjWlZm?=
=3D
 =3D?utf-8?B?Y1QzRVlxbFV5aU1zZWJBbHVBeUE0RGI3Q05XN2xqYmJkUXo2MDBjS1hBaVBG?=
=3D
 =3D?utf-8?B?dzFHSStGNThkUmRRUXRHUjNZOEJXYzRuVDcydWJQYXBjZUN0bFhTMEhWejZy?=
=3D
 =3D?utf-8?B?SVBlSmNwaGVZMzdVbURjS2xBOGo5M2UzQVFRY2V5Ny9sb3ZCZytPWC9SenVU?=
=3D
 =3D?utf-8?B?YndBWE9pZy9oVFZ2WmttL1crYnNqUEdUOWpReE83UkVPcTBEUitVaElkL2xk?=
=3D
 =3D?utf-8?B?TURvdTV0RjNtVXBNUk5pM25NaC83Z0RCNmJsYkJxRi8vQjN2NURST3E1S2NC?=
=3D
 =3D?utf-8?B?aGh3bHVsR0owcHpuemhMRzh2YThSd1JUbWRWbUJLU2pJTU95RGpHOWNHdk0y?=
=3D
 =3D?utf-8?B?R3RMSzNOK3pqaUVnVDB1dlNPSzJOQUJUbVJsekJUVkE3TjExUWhVOTgzcnRx?=
=3D
 =3D?utf-8?B?L2JMaTQ1OUIweG5SNm5nWU5Hc1lWeGJvZmo0RmEzT3lMSnVjMG1YMktoT1lS?=
=3D
 =3D?utf-8?B?MWxLVkpYN2t3Wk5HZVhHYjQ1bTNJSFR4WUphNGEzNzlhc3dDU0o1ckVvUmdz?=
=3D
 =3D?utf-8?B?SzVmM1lwNzZTOTRkVEw2dkEyUEQ2Y3dFaW85a2tTSmRwTFRRVnBBTDRsQ09x?=
=3D
 =3D?utf-8?B?OHNQZllucjhlQk5TMTl2QnBYREllcHVVYlVnMElhZUkrTGlhd3pHZVlCU0ZO?=
=3D
 =3D?utf-8?B?UzBHcGwwdjlJQmgwN1I4RlFFV0c0cU5jSFZ5TldZUjVmamo0WXZ2TURMUGxu?=
=3D
 =3D?utf-8?B?V2VXY0o1aWtieXRNcmVPUzVFbHl5WEgvVXdwQloraVMybys2Y0RNZEg1cWFW?=
=3D
 =3D?utf-8?B?bDBZQ28yRmZrKzJSa2s0QXJyT29UVnVuVkZoSmI5QktucEVSZG5oRWdiRnJJ?=
=3D
 =3D?utf-8?B?VXFEMFg2RkxSQWNkRXJtS1MrZ2Y3NzE3NVlJUzhNZVN5bzZzb3Zqem1wSHgw?=
=3D
 =3D?utf-8?B?aDEvRUIzTkxuR2hkbkZYMFBEOFMxY3lGZmYzU0JSKzZkMy9vdzcwY25GbzZP?=
=3D
 =3D?utf-8?B?Y3MzSmV6MVNkNGlLNnFtd0lZMDh1QXl4NGI0NzNZT3J6YnJaRWZoV3U4ODJJ?=
=3D
 =3D?utf-8?B?ZCtyYXJwbXlKelRpYi9wNDVkM3JKSkFIRVpCSmNkVWpBOEdpQUJ6RlJYanlr?=
=3D
 =3D?utf-8?Q?6o/VXCmuy/TtOi1HEkY9LalZ4N1NY=3D3D?=3D
X-Exchange-RoutingPolicyChecked:
	pwiwLGDNtf8BNJDlAYItR55dkzMV0CE4fSCh5JzDomz1k+nPl+6APl0XS8jXDwWPsZJD/pBHWf=
Yfx5mD6WoJQ1nXi7FDot+wfLP+/NX6KpTkY1FrLp1WVU8TWvnYs0B2nZxdv7e6Cesd6GJ/0A2/Y=
ECV4mMMMx3nGiW/AgjQen9malNu+QzeE2D5Q81TOIlq79M8L4lhnmXdt4gw2ySTMIyf03akVsI3=
Rt8pMKW9P7CldzCE/SxdHTNlU4Qx0F5iYy7H79ctEd4jO2B1SgOyxoC6sLyjqDoVCE06PtgjN7z=
J6DE3DaGRgOwAhKQ3N+ELYvRNyUw8CDDGdn6z/y9NeA=3D=3D
X-OriginatorOrg: microsoft.onmicrosoft.com
X-MS-Exchange-CrossTenant-OriginalArrivalTime: 02 Oct 2026 15:08:28.6118
 (UTC)
X-MS-Exchange-CrossTenant-Network-Message-Id: 42036b4f-3986-461f-d565-08df2=
09703de
X-MS-Exchange-CrossTenant-Id: 72f988bf-86f1-41af-91ab-2d7cd011db47
X-MS-Exchange-CrossTenant-AuthSource:
	MWH0EPF000C6192.namprd02.prod.outlook.com
X-MS-Exchange-CrossTenant-AuthAs: Anonymous
X-MS-Exchange-CrossTenant-FromEntityHeader: Internet
X-MS-Exchange-Transport-CrossTenantHeadersStamped: LV0PR21MB6142
