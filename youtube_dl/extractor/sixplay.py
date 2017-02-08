# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    determine_ext,
    int_or_none,
    try_get,
    qualities,
)


class SixPlayIE(InfoExtractor):
    _VALID_URL = r'(?:6play:|https?://(?:www\.)?6play\.fr/.+?-c_)(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.6play.fr/le-meilleur-patissier-p_1807/le-meilleur-patissier-special-fetes-mercredi-a-21-00-sur-m6-c_11638450',
        'md5': '42310bffe4ba3982db112b9cd3467328',
        'info_dict': {
            'id': '11638450',
            'ext': 'mp4',
            'title': 'Le Meilleur Pâtissier, spécial fêtes mercredi à 21:00 sur M6',
            'description': 'md5:308853f6a5f9e2d55a30fc0654de415f',
            'duration': 39,
            'series': 'Le meilleur pâtissier',
        },
        'params': {
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        data = self._download_json(
            'https://pc.middleware.6play.fr/6play/v2/platforms/m6group_web/services/6play/videos/clip_%s' % video_id,
            video_id, query={
                'csa': 5,
                'with': 'clips',
            })

        clip_data = data['clips'][0]
        title = clip_data['title']

        quality_key = qualities(['lq', 'sd', 'hq', 'hd'])
        formats = []
        for asset in clip_data['assets']:
            asset_url = asset.get('full_physical_path')
            if not asset_url:
                continue
            container = asset.get('video_container')
            ext = determine_ext(asset_url)
            if container == 'm3u8' or ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    asset_url, video_id, 'mp4', 'm3u8_native',
                    m3u8_id='hls', fatal=False))
                formats.extend(self._extract_f4m_formats(
                    asset_url.replace('.m3u8', '.f4m'),
                    video_id, f4m_id='hds', fatal=False))
            elif container == 'mp4' or ext == 'mp4':
                quality = asset.get('video_quality')
                formats.append({
                    'url': asset_url,
                    'format_id': quality,
                    'quality': quality_key(quality),
                    'ext': ext,
                })
        self._sort_formats(formats)

        def get(getter):
            for src in (data, clip_data):
                v = try_get(src, getter, compat_str)
                if v:
                    return v

        return {
            'id': video_id,
            'title': title,
            'description': get(lambda x: x['description']),
            'duration': int_or_none(clip_data.get('duration')),
            'series': get(lambda x: x['program']['title']),
            'formats': formats,
        }