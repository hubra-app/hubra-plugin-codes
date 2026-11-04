import { registerPlugin } from '@hubra/plugin-sdk'
import { CodesScreen } from './CodesScreen'
import translations from './translations.json'

registerPlugin({
  id: 'codes',
  routes: [
    {
      path: 'operations/codes',
      module: 'codes',
      perm: 'codes.codes.read',
      component: CodesScreen,
    },
  ],
  translations,
})
