/* Peças-base do Rétrovisage (aprovadas no gancho de fda-2026-11-04-retrovisage02, 04/11).
   Uso: <script src="assets/pecas.js"></script> depois do GSAP; o CSS está em pecas.css.
   Todas recebem a timeline (tl) e tempos absolutos; tudo é determinístico (sorteio com semente). */
(function(){
  const L = {lazy:false};
  // ---------- sorteio com semente ----------
  function sorteio(seed){ return () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }; }

  // ---------- PÁLPEBRAS: fecham e abrem com uma piscada ----------
  // HTML: <div id="palpebra" class="rv-palpebra"></div> (por cima das cenas)
  function palpebras(tl, el, {fecha=0, fechaDur=1.0, abre=1.35} = {}){
    tl.fromTo(el,{'--h':'150%'},{'--h':'0%',duration:fechaDur,ease:'sine.inOut',...L},fecha);
    tl.fromTo(el,{'--h':'0%'},{'--h':'38%',duration:.6,ease:'power2.out',immediateRender:false,...L},abre);
    tl.fromTo(el,{'--h':'38%'},{'--h':'24%',duration:.22,ease:'sine.inOut',immediateRender:false,...L},abre+.6);
    tl.fromTo(el,{'--h':'24%'},{'--h':'150%',duration:1.0,ease:'power2.inOut',immediateRender:false,...L},abre+.82);
  }

  // ---------- RELÓGIO DE ESCOLA desenhado; ponteiros voltam no tempo ----------
  // relogio(container, {legenda}) desenha; ponteirosVoltam(tl, t, dur, horaFinal, minFinal, voltas)
  function relogio(container, {legenda='ÉCOLE COMMUNALE', cx=960, cy=545} = {}){
    let s=`<svg width="1920" height="1080" style="position:absolute;left:0;top:0"><g transform="translate(${cx} ${cy}) rotate(-3)">
      <circle r="352" fill="#3a2216" opacity=".25" transform="translate(10 14)"/>
      <circle r="345" fill="#4A2C1D"/><circle r="312" fill="#F7EEDB"/><circle r="296" fill="none" stroke="#4A2C1D" stroke-width="3"/>`;
    for(let i=0;i<60;i++){const L=i%5===0?26:12, w=i%5===0?7:3; s+=`<line x1="0" y1="-292" x2="0" y2="${-292+L}" stroke="#4A2C1D" stroke-width="${w}" transform="rotate(${i*6})"/>`;}
    for(let h=1;h<=12;h++){const a=h*30*Math.PI/180; s+=`<text x="${(Math.sin(a)*228).toFixed(1)}" y="${(-Math.cos(a)*228+24).toFixed(1)}" text-anchor="middle" font-family="Playfair Display" font-weight="700" font-size="70" fill="#4A2C1D">${h}</text>`;}
    s+=`<text x="0" y="110" text-anchor="middle" font-family="Special Elite" font-size="30" fill="#4A2C1D" opacity=".7">${legenda}</text>
      <g class="rv-pH"><path d="M-14 30 L-9 -150 L0 -172 L9 -150 L14 30 Z" fill="#4A2C1D"/></g>
      <g class="rv-pM"><path d="M-9 40 L-6 -250 L0 -270 L6 -250 L9 40 Z" fill="#4A2C1D"/></g>
      <circle r="20" fill="#D9622B"/><circle r="7" fill="#4A2C1D"/></g></svg>`;
    container.innerHTML = s;
  }
  function ponteirosVoltam(tl, container, t, dur, hora=8, min=30, voltas=3){
    const pM = container.querySelector('.rv-pM'), pH = container.querySelector('.rv-pH');
    const mF = min*6, hF = (hora%12)*30 + min*.5;
    tl.set(pM,{rotation:mF+voltas*360,svgOrigin:'0 0'},0); tl.set(pH,{rotation:hF+voltas*30,svgOrigin:'0 0'},0);
    tl.fromTo(pM,{rotation:mF+voltas*360},{rotation:mF,duration:dur,ease:'power3.inOut',svgOrigin:'0 0',immediateRender:false,...L},t);
    tl.fromTo(pH,{rotation:hF+voltas*30},{rotation:hF,duration:dur,ease:'power3.inOut',svgOrigin:'0 0',immediateRender:false,...L},t);
  }

  // ---------- FOLHA DE BORDA RASGADA atravessando a tela ----------
  // HTML: <div class="rv-folha" style="background:#4A2C1D"></div> dentro de uma camada de quadro inteiro
  // lado: 'direita' (vem da direita, borda rasgada à esquerda) ou 'baixo' (sobe, borda rasgada em cima)
  function folhaRasgada(tl, el, t, {lado='direita', dur=.5, semente=7} = {}){
    const r = sorteio(semente), p = [];
    if(lado==='direita'){
      Object.assign(el.style,{position:'absolute',top:'-40px',left:'0',width:'2400px',height:'1160px'});
      p.push('100% 0','100% 100%'); for(let y=100;y>=0;y-=2.5) p.push(`${(r()*46).toFixed(1)}px ${y}%`);
      el.style.clipPath=`polygon(${p.join(',')})`;
      tl.fromTo(el,{x:1960},{x:-60,duration:dur,ease:'power3.inOut',...L},t);
    } else {
      Object.assign(el.style,{position:'absolute',left:'-40px',top:'0',width:'2000px',height:'1500px'});
      p.push('0 100%','100% 100%'); for(let x=100;x>=0;x-=1.8) p.push(`${x}% ${(r()*46).toFixed(1)}px`);
      el.style.clipPath=`polygon(${p.join(',')})`;
      tl.fromTo(el,{y:1120},{y:-40,duration:dur,ease:'power3.inOut',...L},t);
    }
  }

  // ---------- MANCHA DE TINTA: gota cai, espalha e toma a tela ----------
  // HTML: <svg class="rv-mancha" width="400" height="400" viewBox="-200 -200 400 400"><path fill="#5B2A86"/></svg>
  // Depois, a cena nova pode se abrir de dentro dela com clipPath circle (ver catalogo.md).
  function mancha(tl, svg, t, {cobre=.75, escala=10, some=null, semente=3} = {}){
    const r = sorteio(semente), n = 22, R = 150, pts = [];
    for(let i=0;i<n;i++){const a=i/n*Math.PI*2, rr=R*(1+(r()-.5)*.35); pts.push([Math.cos(a)*rr,Math.sin(a)*rr]);}
    let d=''; const z=pts[n-1]; d+=`M${((z[0]+pts[0][0])/2).toFixed(1)} ${((z[1]+pts[0][1])/2).toFixed(1)} `;
    for(let i=0;i<n;i++){const p=pts[i],q=pts[(i+1)%n]; d+=`Q${p[0].toFixed(1)} ${p[1].toFixed(1)} ${((p[0]+q[0])/2).toFixed(1)} ${((p[1]+q[1])/2).toFixed(1)} `;}
    svg.querySelector('path').setAttribute('d', d+'Z');
    tl.set(svg,{visibility:'visible'},t);
    tl.fromTo(svg,{scale:0},{scale:.5,duration:.28,ease:'back.out(2)',...L},t);
    tl.fromTo(svg,{scale:.5},{scale:escala,duration:.45,ease:'power2.in',immediateRender:false,...L},t+.3);
    if(some!=null){ tl.fromTo(svg,{opacity:1},{opacity:0,duration:.33,immediateRender:false,...L},some); tl.set(svg,{visibility:'hidden'},some+.35); }
  }

  // ---------- POLAROIDES + CONTADOR: caem acelerando; o número chega no número dito ----------
  // fotos: lista de caminhos; num: elemento do número; tFim: tempo da palavra do número
  function polaroides(tl, container, num, fotos, t0, tFim, {semente=20261104, centroY=650} = {}){
    const r = sorteio(semente), els = [], N = fotos.length;
    fotos.forEach((src,i)=>{
      const arco=i%2, k=Math.floor(i/2), passos=Math.ceil(N/2)-1||1;
      const ang=(-80+k*(160/passos))*Math.PI/180, R=arco?470:610, Ry=arco?300:395;
      const cx=960+Math.sin(ang)*R, cy=centroY-Math.cos(ang)*Ry*.9+(arco?40:60), rot=(r()-.5)*24;
      const el=document.createElement('div'); el.className='foto rv-pola';
      el.style.cssText=`left:${(cx-105).toFixed(0)}px;top:${(cy-125).toFixed(0)}px;width:210px;padding:12px 12px 44px;transform:rotate(${rot.toFixed(1)}deg)`;
      el.innerHTML=`<div class="janela" style="width:186px;height:186px;background:#efe6d2"><img src="${src}" class="pb" style="width:100%;height:100%;object-fit:cover;left:0;top:0"></div>`;
      container.appendChild(el); els.push([el,rot]);
    });
    els.forEach(([el,rot],i)=>{
      const f=i/(N-1), t=t0+(tFim-t0)*(1-Math.pow(1-f,1.6));
      tl.fromTo(el,{y:-380,x:(i%2?1:-1)*60,rotation:rot+(i%2?25:-25),opacity:0,scale:1.25},{y:0,x:0,rotation:rot,opacity:1,scale:1,duration:.32,ease:'back.out(1.4)',...L},t);
      if(i>0) tl.set(num,{textContent:String(i+1)},t+.12);
    });
  }

  window.RV = {sorteio, palpebras, relogio, ponteirosVoltam, folhaRasgada, mancha, polaroides};
})();
